import datetime
from urllib.error import HTTPError
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.encoders import jsonable_encoder
from kubernetes.client import ApiClient, CoreV1Api, CustomObjectsApi
from kubernetes.client.rest import ApiException as K8sAPIException
from kubernetes.client.rest import RESTResponse
from pymongo.errors import DuplicateKeyError
from yaml import safe_load

from ..config.config import config
from ..internal.auth import get_current_user
from ..internal.db import get_db
from ..internal.k8s_client import get_k8s_client
from ..internal.templates import template_env
from ..internal.utils import k8s_safe_name, uncased_to_snake_case
from ..models.engine import (
    CreateInferenceEngineService,
    InferenceEngineService,
    UpdateInferenceEngineService,
)
from ..models.iam import TokenData

router = APIRouter(prefix="/engines", tags=["Inference Engines"])


@router.get("/{service_name}")
async def get_inference_engine_service(
    service_name: str,
    db=Depends(get_db),
):
    db, _ = db
    service = await db["services"].find_one({"serviceName": service_name})
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return service


@router.get("/{service_name}/status")
def get_inference_engine_service_status(
    service_name: str, k8s_client: ApiClient = Depends(get_k8s_client)
):
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
            return result["status"]
    except K8sAPIException as e:
        if e.status == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service {service_name} not found",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting service status",
        )


@router.get("/")
async def get_available_inference_engine_services(
    k8s_client: ApiClient = Depends(get_k8s_client),
):
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
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API has no access to the K8S cluster",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {e}",
        )


@router.post("/")
async def create_inference_engine_service(
    service: CreateInferenceEngineService,
    k8s_client: ApiClient = Depends(get_k8s_client),
    db=Depends(get_db),
    user: TokenData = Depends(get_current_user),
):
    # First check that model actually exists in DB
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
                "resource_limits": service.resource_limits.dict(),
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
        lb_ip = kourier_ingress.status.load_balancer.ingress[0].ip
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
                    ),  # conver title to ID
                    created=datetime.datetime.now(),
                    last_modified=datetime.datetime.now(),
                    inference_url=url,
                    service_name=service_name,
                    resource_limits=service.resource_limits,
                ),
                by_alias=True,  # convert snake_case to camelCase
            )

            async with await mongo_client.start_session() as session:
                async with session.start_transaction():
                    await db["services"].insert_one(service_metadata)
            return service_metadata
        except (K8sAPIException, HTTPError) as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error when creating inference engine: {e}",
            )
        except TypeError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"API has no access to the K8S cluster: {e}",
            )
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unable to add duplicate service",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error when creating inference engine: {e}",
            )


@router.delete("/cleanup", status_code=status.HTTP_204_NO_CONTENT)
async def delete_orphan_services(
    db=Depends(get_db), k8s_client: ApiClient = Depends(get_k8s_client)
):
    db, mongo_client = db
    # Get all model cards
    model_services = await (
        db["models"].find(
            {}, {"inferenceServiceName": 1}  # include only service names
        )
    ).to_list(length=None)
    # Do a search of all services NOT IN modelServices
    orphaned_services = db["services"].find(
        {
            "serviceName": {
                "$nin": [x["inferenceServiceName"] for x in model_services]
            }
        },
        {"serviceName": 1},
    )
    with k8s_client as client:
        api = CustomObjectsApi(client)
        async with await mongo_client.start_session() as session:
            async for service in orphaned_services:
                # Remove service
                service_name = service["serviceName"]
                async with session.start_transaction():

                    try:
                        await db["services"].delete_one(
                            {"serviceName": service_name}
                        )
                        api.delete_namespaced_custom_object(
                            group="serving.knative.dev",
                            version="v1",
                            plural="services",
                            namespace=config.IE_NAMESPACE,
                            name=service_name,
                        )
                    except K8sAPIException as e:
                        if e.status == 404:
                            # Service not present
                            continue
                    except HTTPError as e:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error when deleting inference engine: {e}",
                        )
                    except TypeError:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="API has no access to the K8S cluster",
                        )
                    except Exception as e:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error when deleting inference engine: {e}",
                        )


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
                except (K8sAPIException, HTTPError) as e:
                    session.abort_transaction()  # if failed to remove in k8s, rollback db change
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error when deleting inference engine: {e}",
                    )
                except TypeError:
                    session.abort_transaction()
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="API has no access to the K8S cluster",
                    )
                except Exception as e:
                    session.abort_transaction()
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error when deleting inference engine: {e}",
                    )


@router.patch("/{service_name}")
async def update_inference_engine_service(
    service_name: str,
    service: UpdateInferenceEngineService,
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
                    except (K8sAPIException, HTTPError) as e:
                        session.abort_transaction()
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error when updating inference engine: {e}",
                        )
                    except TypeError:
                        session.abort_transaction()
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="API has no access to the K8S cluster",
                        )
                    except Exception as e:
                        session.abort_transaction()
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error when updating inference engine: {e}",
                        )
