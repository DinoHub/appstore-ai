"""Endpoints for Inference Engine Services"""
import datetime
from typing import Dict, Tuple
from urllib.error import HTTPError
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, status
from fastapi.encoders import jsonable_encoder
from kubernetes.client import ApiClient, CoreV1Api, CustomObjectsApi
from kubernetes.client.rest import ApiException as K8sAPIException
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from yaml import safe_load

from ..config.config import config
from ..internal.auth import get_current_user
from ..internal.db import get_db
from ..internal.k8s_client import get_k8s_client
from ..internal.tasks import delete_orphan_services
from ..internal.templates import template_env
from ..internal.utils import k8s_safe_name, uncased_to_snake_case
from ..models.engine import (
    CreateInferenceEngineService,
    InferenceEngineService,
    UpdateInferenceEngineService,
)
from ..models.iam import TokenData

router = APIRouter(prefix="/engines", tags=["Inference Engines"])


@router.get("/{service_name}", response_model=InferenceEngineService)
async def get_inference_engine_service(
    service_name: str,
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
) -> Dict:
    """Get Inference Engine Service

    Args:
        service_name (str): Name of the service
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB connection.
            Defaults to Depends(get_db).

    Raises:
        HTTPException: 404 Not Found if service does not exist

    Returns:
        Dict: Service details
    """
    db, _ = db
    service = await db["services"].find_one({"serviceName": service_name})
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return service


@router.get("/{service_name}/status")
def get_inference_engine_service_status(
    service_name: str, k8s_client: ApiClient = Depends(get_k8s_client)
) -> Dict:
    """Get status of an inference service. This is typically
    used to give liveness/readiness probes for the service.

    Args:
        service_name (str): Name of the service
        k8s_client (ApiClient, optional): K8S Client. Defaults to Depends(get_k8s_client).

    Raises:
        HTTPException: 404 Not Found if service does not exist
        HTTPException: 500 Internal Server Error if there is an error getting the service status

    Returns:
        Dict: Service status
    """
    # Sync endpoint to allow for concurrent request
    try:
        with k8s_client as client:
            api = CustomObjectsApi(client)
            result = api.get_namespaced_custom_object(
                group="serving.knative.dev",
                version="v1",
                namespace=config.IE_NAMESPACE,
                plural="services",
                name=service_name,
            )
            return result["status"]  # type: ignore
    except K8sAPIException as err:
        if err.status == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service {service_name} not found",
            ) from err
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting service status",
        ) from err


@router.get("/")
async def get_available_inference_engine_services(
    k8s_client: ApiClient = Depends(get_k8s_client),
):
    """Get all available inference engine services

    Args:
        k8s_client (ApiClient, optional): K8S client. Defaults to Depends(get_k8s_client).

    Raises:
        HTTPException: 500 Internal Server Error if there is an error getting the services
        HTTPException: 500 Internal Server Error if the API has no access to the K8S cluster

    Returns:
        Object: List of services # TODO: Figure out what type this is
    """
    try:
        with k8s_client as client:
            api = CustomObjectsApi(client)
            results = api.list_namespaced_custom_object(
                group="serving.knative.dev",
                version="v1",
                namespace=config.IE_NAMESPACE,
                plural="services",
            )
        return results
    except TypeError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API has no access to the K8S cluster",
        ) from err
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


@router.post("/", response_model=InferenceEngineService)
async def create_inference_engine_service(
    service: CreateInferenceEngineService,
    k8s_client: ApiClient = Depends(get_k8s_client),
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
    user: TokenData = Depends(get_current_user),
) -> Dict:
    """Create an inference engine service

    Args:
        service (CreateInferenceEngineService): Service details
        k8s_client (ApiClient, optional): K8S client. Defaults to Depends(get_k8s_client).
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB connection.
            Defaults to Depends(get_db).
        user (TokenData, optional): User details. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 500 Internal Server Error if there is an error creating the service
        HTTPException: 500 Internal Server Error if the API has no access to the K8S cluster
        HTTPException: 500 Internal Server Error if there is an error creating the service in the DB
        HTTPException: 422 Unprocessable Entity if the service already exists
        HTTPException: 422 Unprocessable Entity if the namespace is not set

    Returns:
        Dict: Service details
    """
    # Create Deployment Template
    if not user.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    template = template_env.get_template("inference-engine-service.yaml.j2")
    service_name = k8s_safe_name(
        f"{user.user_id}-{service.model_id}-{uuid4()}"
    )
    deployment_template = safe_load(
        template.render(
            {
                "engine_name": service_name,
                "image_name": service.image_uri,
                "port": service.container_port,
                "env": service.env,
                # "resource_limits": service.resource_limits.dict(),
            }
        )
    )
    if not config.IE_NAMESPACE:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No Namespace specified",
        )
    # Deploy Service on K8S
    with k8s_client as client:
        # Get KNative Serving Ext Ip
        core_api = CoreV1Api(client)
        kourier_ingress = core_api.read_namespaced_service(
            name="kourier", namespace="knative-serving"
        )
        lb_ip = kourier_ingress.status.load_balancer.ingress[0].ip  # type: ignore
        if service.external_dns:
            # TODO: Support for https
            url = f"http://{service_name}.{config.IE_NAMESPACE}.{service.external_dns}"
        else:
            url = (
                f"http://{service_name}.{config.IE_NAMESPACE}.{lb_ip}.sslip.io"
            )
        # Create instance of API class
        api = CustomObjectsApi(client)
        try:
            api.create_namespaced_custom_object(
                group="serving.knative.dev",
                version="v1",
                plural="services",
                namespace=config.IE_NAMESPACE,
                body=deployment_template,
            )
            # Save info into DB
            db, mongo_client = db
            service_metadata = jsonable_encoder(
                InferenceEngineService(
                    image_uri=service.image_uri,
                    container_port=service.container_port,
                    env=service.env,
                    external_dns=service.external_dns,
                    owner_id=user.user_id,
                    model_id=uncased_to_snake_case(
                        service.model_id
                    ),  # convert title to ID
                    created=datetime.datetime.now(),
                    last_modified=datetime.datetime.now(),
                    inference_url=url,
                    service_name=service_name,
                    # resource_limits=service.resource_limits,
                ),
                by_alias=True,  # convert snake_case to camelCase
            )

            async with await mongo_client.start_session() as session:
                async with session.start_transaction():
                    await db["services"].insert_one(service_metadata)
            return service_metadata
        except (K8sAPIException, HTTPError) as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error when creating inference engine: {err}",
            ) from err
        except TypeError as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"API has no access to the K8S cluster: {err}",
            ) from err
        except DuplicateKeyError as err:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Duplicate service name",
            ) from err
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error when creating inference engine: {err}",
            ) from err


@router.delete("/{service_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inference_engine_service(
    service_name: str = Path(description="Name of KService to Delete"),
    k8s_client: ApiClient = Depends(get_k8s_client),
    db=Depends(get_db),
    user: TokenData = Depends(get_current_user),
):
    """Delete a deployed inference engine from the K8S cluster.

    :param service_name: Name of KNative service, defaults to Path(description="Name of KService to Delete")
    :type service_name: str, optional
    :param k8s_client: Python K8S Client, defaults to Depends(get_k8s_client)
    :type k8s_client: ApiClient, optional
    :raises HTTPException: 500 Internal Server Error if deletion fails
    """

    ## Get User ID from Request
    db, mongo_client = db
    async with await mongo_client.start_session() as session:
        async with session.start_transaction():
            # Check user has access to service
            existing_service = await db["services"].find_one(
                {"serviceName": service_name}
            )
            if (
                existing_service is not None
                and existing_service["ownerId"] != user.user_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have owner access to KService",
                )
            await db["services"].delete_one({"serviceName": service_name})
            with k8s_client as client:
                # Create instance of API class
                api = CustomObjectsApi(client)
                try:
                    api.delete_namespaced_custom_object(
                        group="serving.knative.dev",
                        version="v1",
                        plural="services",
                        namespace=config.IE_NAMESPACE,
                        name=service_name,
                    )
                except (K8sAPIException, HTTPError) as err:
                    session.abort_transaction()  # if failed to remove in k8s, rollback db change
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error when deleting inference engine: {err}",
                    ) from err
                except TypeError as err:
                    session.abort_transaction()
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="API has no access to the K8S cluster",
                    ) from err
                except Exception as err:
                    session.abort_transaction()
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error when deleting inference engine: {err}",
                    ) from err


@router.patch("/{service_name}")
async def update_inference_engine_service(
    service_name: str,
    service: UpdateInferenceEngineService,
    tasks: BackgroundTasks,
    k8s_client: ApiClient = Depends(get_k8s_client),
    db=Depends(get_db),
    user: TokenData = Depends(get_current_user),
):
    """Update an existing inference engine inside the K8S cluster

    :param service: Configuration (service name and Image URI) of updated Inference Engine
    :type service: InferenceEngineService
    :param k8s_client: Python K8S client, defaults to Depends(get_k8s_client)
    :type k8s_client: ApiClient, optional
    :raises HTTPException: 500 Internal Server Error if failed to update
    """
    # Create Deployment Template
    tasks.add_task(
        delete_orphan_services
    )  # Remove preview services created in testing
    db, mongo_client = db
    updated_metadata = {
        k: v for k, v in service.dict(by_alias=True).items() if v is not None
    }

    if len(updated_metadata) > 0:
        updated_metadata["lastModified"] = str(datetime.datetime.now())
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                # Check if user has editor access
                existing_service = await db["services"].find_one(
                    {"serviceName": service_name}
                )
                if existing_service is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"KService with name {service_name} not found",
                    )
                elif existing_service["ownerId"] != user.user_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="User does not have owner access to KService",
                    )
                result = await db["services"].update_one(
                    {"serviceName": service_name}, {"$set": updated_metadata}
                )
                updated_service = await db["services"].find_one(
                    {"serviceName": service_name}
                )
                if result.modified_count != 1:
                    # Not necessary to update service?
                    return updated_service
                template = template_env.get_template(
                    "inference-engine-service.yaml.j2"
                )
                deployment_template = safe_load(
                    template.render(
                        {
                            "engine_name": service_name,
                            "image_name": updated_service["imageUri"],
                            "port": updated_service["containerPort"],
                            "env": updated_service["env"],
                        }
                    )
                )
                # Deploy Service on K8S
                with k8s_client as client:
                    # Create instance of API class
                    api = CustomObjectsApi(client)
                    try:
                        api.patch_namespaced_custom_object(
                            group="serving.knative.dev",
                            version="v1",
                            plural="services",
                            namespace=config.IE_NAMESPACE,
                            name=service_name,
                            body=deployment_template,
                        )
                        return updated_service
                    except (K8sAPIException, HTTPError) as err:
                        session.abort_transaction()
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error when updating inference engine: {err}",
                        ) from err
                    except TypeError as err:
                        session.abort_transaction()
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="API has no access to the K8S cluster",
                        ) from err
                    except Exception as err:
                        session.abort_transaction()
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error when updating inference engine: {err}",
                        ) from err
