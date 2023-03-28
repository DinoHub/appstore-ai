"""Endpoints for Inference Engine Services"""
import asyncio
import datetime
from typing import Dict, Tuple
from urllib.error import HTTPError
from uuid import uuid4

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Path,
    Request,
    status,
)
from fastapi.encoders import jsonable_encoder
from kubernetes.client import ApiClient, AppsV1Api, CoreV1Api, CustomObjectsApi
from kubernetes.client.rest import ApiException as K8sAPIException
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from sse_starlette.sse import EventSourceResponse
from yaml import safe_load

from ..config.config import config
from ..internal.auth import get_current_user
from ..internal.dependencies.k8s_client import get_k8s_client
from ..internal.dependencies.mongo_client import get_db
from ..internal.tasks import delete_orphan_services
from ..internal.templates import template_env
from ..internal.utils import k8s_safe_name, uncased_to_snake_case
from ..models.engine import (
    CreateInferenceEngineService,
    InferenceEngineService,
    InferenceServiceStatus,
    ServiceBackend,
    UpdateInferenceEngineService,
)
from ..models.iam import TokenData, UserRoles

router = APIRouter(prefix="/engines", tags=["Inference Engines"])


@router.get("/{service_name}/logs")
async def get_inference_engine_service_logs(
    service_name: str,
    request: Request,
    k8s_client: ApiClient = Depends(get_k8s_client),
    db=Depends(get_db),
    user: TokenData = Depends(get_current_user),
) -> EventSourceResponse:
    """Get logs for an inference service

    Args:
        service_name (str): Name of the service
        request (Request): FastAPI Request object
        k8s_client (ApiClient, optional): K8S Client. Defaults to Depends(get_k8s_client).

    Raises:
        HTTPException: 404 Not Found if service does not exist
        HTTPException: 500 Internal Server Error if there is an error getting the service logs

    Returns:
        EventSourceResponse: SSE response with logs
    """
    db, _ = db
    existing_service = await db["services"].find_one(
        {"serviceName": service_name}
    )
    if (
        existing_service is not None
        and existing_service["ownerId"] != user.user_id
        and user.role != UserRoles.admin
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have owner access to KService",
        )
    with k8s_client:
        core_v1 = CoreV1Api(k8s_client)
        # Get pod name
        try:
            pod = core_v1.list_namespaced_pod(
                namespace=config.IE_NAMESPACE,
                label_selector=f"app={service_name}",
            )
            if len(pod.items) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Service not found",
                )
            pod_name = pod.items[0].metadata.name
        except K8sAPIException as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting service logs: {err}",
            ) from err

        async def event_streamer():
            while True:
                # If the client disconnects, stop the stream
                if await request.is_disconnected():
                    break
                logs = core_v1.read_namespaced_pod_log(
                    name=pod_name, namespace=config.IE_NAMESPACE, pretty=True
                )
                yield logs
                await asyncio.sleep(5)

        return EventSourceResponse(event_streamer())


@router.patch("/{service_name}/scale/{replicas}")
async def scale_inference_engine_deployments(
    service_name: str,
    replicas: int = Path(ge=0, le=3),
    k8s_client: ApiClient = Depends(get_k8s_client),
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
) -> Dict:
    """Scale the number of replicas of the deployment

    Args:
        service_name (str): Name of the service
        replicas (int, optional): Number of replicas. Defaults to Path(ge=0, le=3).
        k8s_client (ApiClient, optional): K8S Client. Defaults to Depends(get_k8s_client).

    Raises:
        HTTPException: 404 Not Found if service does not exist
        HTTPException: 500 Internal Server Error if there is an error scaling the service
    """
    with k8s_client:
        apps_v1 = AppsV1Api(k8s_client)
        db, _ = db
        service = await db["services"].find_one({"serviceName": service_name})
        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found",
            )
        # Scale deployment
        # Check type of service
        if service["backend"] == ServiceBackend.EMISSARY:
            try:
                apps_v1.patch_namespaced_deployment_scale(
                    name=service_name + "-deployment",
                    namespace=config.IE_NAMESPACE,
                    body={"spec": {"replicas": replicas}},
                )
                return {
                    "message": "Deployment scaled successfully",
                    "replicas": replicas,
                }
            except K8sAPIException as err:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error scaling deployment: {err}",
                ) from err


@router.get("/{service_name}", response_model=InferenceEngineService)
async def get_inference_engine_service(
    service_name: str,
    k8s_client: ApiClient = Depends(get_k8s_client),
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
        )
    try:
        if "protocol" not in service:
            protocol = config.IE_DEFAULT_PROTOCOL
        else:
            protocol = service["protocol"]
        path = service["path"]
        # Deploy Service on K8S
        with k8s_client as client:
            # Get KNative Serving Ext Ip
            core_api = CoreV1Api(client)
            service_backend = config.IE_SERVICE_TYPE or ServiceBackend.EMISSARY
            if config.IE_DOMAIN:
                host = config.IE_DOMAIN
            else:
                if service_backend == ServiceBackend.KNATIVE:
                    ingress_name = "kourier"
                    ingress_namespace = "kourier-system"
                elif service_backend == ServiceBackend.EMISSARY:
                    ingress_name = "emissary-ingress"
                    ingress_namespace = "emissary"
                else:
                    if config.IE_INGRESS_NAME and config.IE_INGRESS_NAMESPACE:
                        ingress_name = config.IE_INGRESS_NAME
                        ingress_namespace = config.IE_INGRESS_NAMESPACE
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="No Ingress specified",
                        )
                ingress = core_api.read_namespaced_service(
                    name=ingress_name, namespace=ingress_namespace
                )
                host = ingress.status.load_balancer.ingress[0].ip
        # Generate service url
        if service_backend == ServiceBackend.EMISSARY:
            url = f"{protocol}://{host}/{path}/"  # need to add trailing slash for ambassador
        elif service_backend == ServiceBackend.KNATIVE:
            url = f"{protocol}://{service_name}.{config.IE_NAMESPACE}.{host}"
            if not config.IE_DOMAIN:
                # use sslip dns service to get a hostname for the service
                url += ".sslip.io"
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid Service Backend",
            )
        service["inferenceUrl"] = url
    except K8sAPIException as err:
        print(f"Error getting service url: {err}")
        print("Defaulting to inference URL specified in database")
    return service


@router.get("/{service_name}/status", response_model=InferenceServiceStatus)
async def get_inference_engine_service_status(
    service_name: str,
    k8s_client: ApiClient = Depends(get_k8s_client),
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
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
    db, _ = db
    try:
        return_status = InferenceServiceStatus(
            service_name=service_name,
        )

        service = await db["services"].find_one({"serviceName": service_name})
        # Get service backend type
        if "backend" in service:
            service_backend = service["backend"]
        else:
            service_backend = config.IE_SERVICE_TYPE
        with k8s_client as client:
            if service_backend == ServiceBackend.KNATIVE:
                api = CustomObjectsApi(client)
                result = api.get_namespaced_custom_object(
                    group="serving.knative.dev",
                    version="v1",
                    namespace=config.IE_NAMESPACE,
                    plural="services",
                    name=service_name,
                )
                status_conditions = result["status"]["conditions"]

                # Check if service is ready
                for condition in status_conditions:
                    # if not ready return response
                    if condition["status"] != "True":
                        return_status.ready = False
                        return_status.message += f"Message: {condition}"
                        break
                # TODO: Check if pod can even be scheduled
            elif service_backend == ServiceBackend.EMISSARY:
                api = AppsV1Api(client)
                # Check that service exists
                service_api = CoreV1Api(client)
                service_api.read_namespaced_service(
                    name=service_name, namespace=config.IE_NAMESPACE
                )
                # Get status
                result = api.read_namespaced_deployment_status(
                    name=service_name + "-deployment",
                    namespace=config.IE_NAMESPACE,
                )
                # Get replicas (expected)
                return_status.expected_replicas = int(
                    result.status.replicas if result.status.replicas else 0
                )
                for condition in result.status.conditions:
                    if condition.status != "True":
                        return_status.ready = False
                        return_status.message += f"Message: {condition.message}\nReason: {condition.reason}"
                # Find out if pods in deployment are schedulable
                # Get pods in deployment
                core_api = CoreV1Api(client)
                pods = core_api.list_namespaced_pod(
                    namespace=config.IE_NAMESPACE,
                    label_selector=f"app={service_name}",
                )
                for pod in pods.items:
                    pod_status = pod.status
                    return_status.status = pod_status.phase
                    for condition in pod_status.conditions:
                        if (
                            condition.type == "PodScheduled"
                            and condition.status != "True"
                        ):
                            return_status.schedulable = False
                            return_status.message += f"Message: {condition.message}\nReason: {condition.reason}"
            else:
                raise NotImplementedError
            return return_status.dict(by_alias=True)
    except K8sAPIException as err:
        if err.status == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service {service_name} not found",
            ) from err
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting service status. {err}",
        ) from err


@router.get("/")
async def get_available_inference_engine_services(
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
) -> list:
    """Get all available inference engine services

    Args:
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional):
            MongoDB Connection. Defaults to Depends(get_db).

    Raises:
        HTTPException: 500 Internal Server Error if there is an error getting the services

    Returns:
        list : List of available services
    """
    try:
        db, _ = db
        services = await db["services"].find().to_list(None)
        return services
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err
    # try:
    #     with k8s_client as client:
    #         api = CustomObjectsApi(client)
    #         results = api.list_namespaced_custom_object(
    #             group="serving.knative.dev",
    #             version="v1",
    #             namespace=config.IE_NAMESPACE,
    #             plural="services",
    #         )
    #     return results
    # except TypeError as err:
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail="API has no access to the K8S cluster",
    #     ) from err
    # except Exception as err:
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail="Internal Server Error",
    #     ) from err


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
    service_name = k8s_safe_name(
        f"{user.user_id}-{service.model_id}"[:40] + f"-{uuid4()}"[:5]
    )  # Limit total length to 45 characters, while avoiding complete truncation
    # of uuid4
    if not config.IE_NAMESPACE:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No Namespace specified",
        )
    protocol = config.IE_DEFAULT_PROTOCOL
    path = service_name
    # Deploy Service on K8S
    with k8s_client as client:
        # Get KNative Serving Ext Ip
        try:
            core_api = CoreV1Api(client)
            custom_api = CustomObjectsApi(client)
            service_backend = config.IE_SERVICE_TYPE or ServiceBackend.EMISSARY
            if config.IE_DOMAIN:
                host = config.IE_DOMAIN
            else:
                if service_backend == ServiceBackend.KNATIVE:
                    ingress_name = "kourier"
                    ingress_namespace = "kourier-system"
                elif service_backend == ServiceBackend.EMISSARY:
                    ingress_name = "emissary-ingress"
                    ingress_namespace = "emissary"
                else:
                    if config.IE_INGRESS_NAME and config.IE_INGRESS_NAMESPACE:
                        ingress_name = config.IE_INGRESS_NAME
                        ingress_namespace = config.IE_INGRESS_NAMESPACE
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="No Ingress specified",
                        )
                ingress = core_api.read_namespaced_service(
                    name=ingress_name, namespace=ingress_namespace
                )
                host = ingress.status.load_balancer.ingress[0].ip
            if service_backend == ServiceBackend.KNATIVE:
                service_template = template_env.get_template(
                    "knative/inference-engine-knative-service.yaml.j2"
                )
                service_render = safe_load(
                    service_template.render(
                        {
                            "engine_name": service_name,
                            "image_name": service.image_uri,
                            "port": service.container_port,
                            "env": service.env,
                            "num_gpus": service.num_gpus,
                        }
                    )
                )
                url = (
                    f"{protocol}://{service_name}.{config.IE_NAMESPACE}.{host}"
                )
                if not config.IE_DOMAIN:
                    # use sslip dns service to get a hostname for the service
                    url += ".sslip.io"
                custom_api.create_namespaced_custom_object(
                    group="serving.knative.dev",
                    version="v1",
                    namespace=config.IE_NAMESPACE,
                    plural="services",
                    body=service_render,
                )
            elif service_backend == ServiceBackend.EMISSARY:
                url = f"{protocol}://{host}/{path}/"  # need to add trailing slash for ambassador
                # else css and js files are not loaded properly
                service_template = template_env.get_template(
                    "ambassador/inference-engine-service.yaml.j2"
                )
                deployment_template = template_env.get_template(
                    "ambassador/inference-engine-deployment.yaml.j2"
                )
                mapping_template = template_env.get_template(
                    "ambassador/ambassador-mapping.yaml.j2"
                )
                service_render = safe_load(
                    service_template.render(
                        {
                            "engine_name": service_name,
                            "port": service.container_port,
                        }
                    )
                )
                deployment_render = safe_load(
                    deployment_template.render(
                        {
                            "engine_name": service_name,
                            "image_name": service.image_uri,
                            "port": service.container_port,
                            "env": service.env,
                            "num_gpus": service.num_gpus,
                        }
                    )
                )
                mapping_render = safe_load(
                    mapping_template.render(
                        {
                            "engine_name": service_name,
                        }
                    )
                )
                app_api = AppsV1Api(client)
                core_api = CoreV1Api(client)
                app_api.create_namespaced_deployment(
                    namespace=config.IE_NAMESPACE, body=deployment_render
                )
                core_api.create_namespaced_service(
                    namespace=config.IE_NAMESPACE, body=service_render
                )
                custom_api.create_namespaced_custom_object(
                    group="getambassador.io",
                    version="v2",
                    namespace=config.IE_NAMESPACE,
                    plural="mappings",
                    body=mapping_render,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Invalid service type",
                )
            # Save info into DB
            db, mongo_client = db
            service_metadata = jsonable_encoder(
                InferenceEngineService(
                    image_uri=service.image_uri,
                    container_port=service.container_port,
                    env=service.env,
                    num_gpus=service.num_gpus,
                    owner_id=user.user_id,
                    protocol=protocol,
                    host=host,
                    path=path,
                    model_id=uncased_to_snake_case(
                        service.model_id
                    ),  # convert title to ID
                    created=datetime.datetime.now(),
                    last_modified=datetime.datetime.now(),
                    inference_url=url,
                    service_name=service_name,
                    backend=service_backend
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
    """
    Delete a deployed inference engine from the K8S cluster.

    Args:
        service_name (str, optional): Name of KNative service, defaults to Path(description="Name of KService to Delete")
        k8s_client (ApiClient, optional): K8S client. Defaults to Depends(get_k8s_client).
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB connection.
            Defaults to Depends(get_db).
        user (TokenData, optional): User details. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 500 Internal Server Error if there is an error deleting the service
        HTTPException: 500 Internal Server Error if the API has no access to the K8S cluster
        HTTPException: 403 Forbidden if user does not have owner access to KService
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
                and user.role != UserRoles.admin
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have owner access to KService",
                )
            # Get the service type
            try:
                service_type: ServiceBackend = existing_service["backend"]
            except TypeError:
                print("Existing service not found")
                service_type = config.IE_SERVICE_TYPE
            await db["services"].delete_one({"serviceName": service_name})
            with k8s_client as client:
                # Create instance of API class
                try:
                    if service_type == ServiceBackend.KNATIVE:
                        api = CustomObjectsApi(client)
                        try:
                            api.delete_namespaced_custom_object(
                                group="serving.knative.dev",
                                version="v1",
                                plural="services",
                                namespace=config.IE_NAMESPACE,
                                name=service_name,
                            )
                        except K8sAPIException as err:
                            if err.status == 404:
                                pass
                            else:
                                raise err
                    elif service_type == ServiceBackend.EMISSARY:
                        # Delete service, mapping, and deployment
                        app_api = AppsV1Api(client)
                        core_api = CoreV1Api(client)
                        custom_api = CustomObjectsApi(client)

                        try:
                            core_api.delete_namespaced_service(
                                namespace=config.IE_NAMESPACE,
                                name=service_name,
                            )
                        except K8sAPIException as err:
                            if err.status == 404:
                                pass
                            else:
                                raise err
                        try:
                            custom_api.delete_namespaced_custom_object(
                                group="getambassador.io",
                                version="v2",
                                plural="mappings",
                                namespace=config.IE_NAMESPACE,
                                name=service_name + "-ingress",
                            )
                        except K8sAPIException as err:
                            if err.status == 404:
                                pass
                            else:
                                raise err
                        try:
                            app_api.delete_namespaced_deployment(
                                namespace=config.IE_NAMESPACE,
                                name=service_name + "-deployment",
                            )
                        except K8sAPIException as err:
                            if err.status == 404:
                                pass
                            else:
                                raise err
                except (K8sAPIException, HTTPError) as err:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error when deleting inference engine: {err}",
                    ) from err
                except TypeError as err:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="API has no access to the K8S cluster",
                    ) from err
                except Exception as err:
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

    Args:
        service_name (str, optional): Name of KNative service, defaults to Path(description="Name of KService to Delete")
        service (UpdateInferenceEngineService) : Configuration (service name and Image URI) of updated Inference Engine
        k8s_client (ApiClient, optional): K8S client. Defaults to Depends(get_k8s_client).
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB connection.
            Defaults to Depends(get_db).
        user (TokenData, optional): User details. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 500 Internal Server Error if there is an error updating the service
        HTTPException: 500 Internal Server Error if the API has no access to the K8S cluster
        HTTPException: 404 Not Found if KService with given name is not found
        HTTPException: 403 Forbidden if user does not have owner access to KService

    Returns:
        Dict: Service details
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
        service_type = config.IE_SERVICE_TYPE
        # Use configured cluster service type
        # NOTE: This overrides the service type in the original service
        # TODO: Find a better way to do this
        updated_metadata["backend"] = service_type
        protocol = config.IE_DEFAULT_PROTOCOL
        if config.IE_DOMAIN:
            host = config.IE_DOMAIN
        else:
            with k8s_client as client:
                core_api = CoreV1Api(client)
                if service_type == ServiceBackend.KNATIVE:
                    ingress_name = "kourier"
                    ingress_namespace = "kourier-system"
                elif service_type == ServiceBackend.EMISSARY:
                    ingress_name = "emissary-ingress"
                    ingress_namespace = "emissary"
                else:
                    if config.IE_INGRESS_NAME and config.IE_INGRESS_NAMESPACE:
                        ingress_name = config.IE_INGRESS_NAME
                        ingress_namespace = config.IE_INGRESS_NAMESPACE
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error when trying to determine hostname of Ingress. Unsupported service type",
                        )
                ingress = core_api.read_namespaced_service(
                    name=ingress_name, namespace=ingress_namespace
                )
                host = ingress.status.load_balancer.ingress[0].ip
        updated_metadata["protocol"] = protocol
        updated_metadata["host"] = host
        if service_type == ServiceBackend.KNATIVE:
            updated_metadata[
                "inferenceUrl"
            ] = f"{protocol}://{service_name}.{config.IE_NAMESPACE}.{host}"
            if not config.IE_DOMAIN:
                updated_metadata["inferenceUrl"] += ".sslip.io"
        elif service_type == ServiceBackend.EMISSARY:
            updated_metadata[
                "inferenceUrl"
            ] = f"{protocol}://{host}/{service_name}/"
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
                elif (
                    existing_service["ownerId"] != user.user_id
                    and user.role != UserRoles.admin
                ):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="User does not have owner access to KService",
                    )
                # Check if service type is changed
                # if so, we need to use replace instead of patch
                recreate_service = (
                    updated_metadata["backend"] != existing_service["backend"]
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
                # Get the backend
                # Deploy Service on K8S
                with k8s_client as client:
                    # Create instance of API class
                    try:
                        core_api = CoreV1Api(client)
                        custom_api = CustomObjectsApi(client)
                        if service_type == ServiceBackend.KNATIVE:
                            template = template_env.get_template(
                                "knative/inference-engine-service.yaml.j2"
                            )
                            service_template = safe_load(
                                template.render(
                                    {
                                        "engine_name": service_name,
                                        "image_name": updated_service[
                                            "imageUri"
                                        ],
                                        "port": updated_service[
                                            "containerPort"
                                        ],
                                        "env": updated_service["env"],
                                        "num_gpus": updated_service["numGpus"],
                                    }
                                )
                            )
                            if recreate_service:
                                # Use replacement strategy to update service
                                custom_api.replace_namespaced_custom_object(
                                    group="serving.knative.dev",
                                    version="v1",
                                    plural="services",
                                    namespace=config.IE_NAMESPACE,
                                    name=service_name,
                                    body=service_template,
                                )
                            else:
                                custom_api.patch_namespaced_custom_object(
                                    group="serving.knative.dev",
                                    version="v1",
                                    plural="services",
                                    namespace=config.IE_NAMESPACE,
                                    name=service_name,
                                    body=service_template,
                                )
                        elif service_type == ServiceBackend.EMISSARY:
                            service_template = template_env.get_template(
                                "ambassador/inference-engine-service.yaml.j2"
                            )
                            deployment_template = template_env.get_template(
                                "ambassador/inference-engine-deployment.yaml.j2"
                            )
                            mapping_template = template_env.get_template(
                                "ambassador/ambassador-mapping.yaml.j2"
                            )
                            service_render = safe_load(
                                service_template.render(
                                    {
                                        "engine_name": service_name,
                                        "port": updated_service[
                                            "containerPort"
                                        ],
                                    }
                                )
                            )
                            deployment_render = safe_load(
                                deployment_template.render(
                                    {
                                        "engine_name": service_name,
                                        "image_name": updated_service[
                                            "imageUri"
                                        ],
                                        "port": updated_service[
                                            "containerPort"
                                        ],
                                        "env": updated_service["env"],
                                        "num_gpus": updated_service["numGpus"],
                                    }
                                )
                            )
                            mapping_render = safe_load(
                                mapping_template.render(
                                    {
                                        "engine_name": service_name,
                                    }
                                )
                            )
                            app_api = AppsV1Api(client)
                            if recreate_service:
                                # Use replacement strategy to update service
                                app_api.replace_namespaced_deployment(
                                    namespace=config.IE_NAMESPACE,
                                    name=service_name + "-deployment",
                                    body=deployment_render,
                                )
                                core_api.replace_namespaced_service(
                                    namespace=config.IE_NAMESPACE,
                                    name=service_name,
                                    body=service_render,
                                )
                                custom_api.replace_namespaced_custom_object(
                                    group="getambassador.io",
                                    version="v2",
                                    plural="mappings",
                                    namespace=config.IE_NAMESPACE,
                                    name=service_name + "-ingress",
                                    body=mapping_render,
                                )
                            else:
                                app_api.patch_namespaced_deployment(
                                    namespace=config.IE_NAMESPACE,
                                    name=service_name + "-deployment",
                                    body=deployment_render,
                                )
                                core_api.patch_namespaced_service(
                                    namespace=config.IE_NAMESPACE,
                                    name=service_name,
                                    body=service_render,
                                )
                                custom_api.patch_namespaced_custom_object(
                                    group="getambassador.io",
                                    version="v2",
                                    plural="mappings",
                                    namespace=config.IE_NAMESPACE,
                                    name=service_name + "-ingress",
                                    body=mapping_render,
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


@router.post("/{service_name}/restore")
async def restore_inference_engine_service(
    service_name: str,
    mongodb: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
    k8s_client: ApiClient = Depends(get_k8s_client),
) -> Dict:
    """Restore a deleted service (i.e someone accidently removed the deployment).
    This will do the following:
    1. Grab information about the service from the database
    2. Call the delete endpoint to delete the service
    3. Call the create endpoint to create the service using the information from the database

    Args:
        service_name (str, optional): Name of KNative service, defaults to Path(description="Name of KService to Delete")
        mongodb (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB connection.
            Defaults to Depends(get_db).
        k8s_client (ApiClient, optional): K8S client. Defaults to Depends(get_k8s_client).

    Raises:
        HTTPException: 500 Internal Server Error if there is an error restoring service

    Returns:
        Dict: Details on status of service restoration
    """
    # TODO: Refactor so that I don't have to repeat code. Preferably factor out
    # stuff into a controller submodule (split up the code for adding to mongodb and k8s)
    # to allow router to simply compose functions together for better reusability of code

    # Get service information from database
    db, _ = mongodb

    service = await db["services"].find_one({"serviceName": service_name})
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
        )
    with k8s_client as client:
        custom_api = CustomObjectsApi(client)
        core_api = CoreV1Api(client)
        app_api = AppsV1Api(client)
        service_backend = service["backend"]
        if service_backend == ServiceBackend.KNATIVE:
            service_template = template_env.get_template(
                "knative/inference-engine-knative-service.yaml.j2"
            )
            service = safe_load(
                service_template.render(
                    {
                        "engine_name": service_name,
                        "image_name": service["imageUri"],
                        "port": service["containerPort"],
                        "env": service["env"],
                        "num_gpus": service["numGpus"],
                    }
                )
            )
            custom_api.create_namespaced_custom_object(
                group="serving.knative.dev",
                version="v1",
                namespace=config.IE_NAMESPACE,
                plural="services",
                body=service,
            )
        elif service_backend == ServiceBackend.EMISSARY:
            service_template = template_env.get_template(
                "ambassador/inference-engine-service.yaml.j2"
            )
            deployment_template = template_env.get_template(
                "ambassador/inference-engine-deployment.yaml.j2"
            )
            mapping_template = template_env.get_template(
                "ambassador/ambassador-mapping.yaml.j2"
            )
            service_render = safe_load(
                service_template.render(
                    {
                        "engine_name": service_name,
                        "port": service["containerPort"],
                    }
                )
            )
            deployment_render = safe_load(
                deployment_template.render(
                    {
                        "engine_name": service_name,
                        "image_name": service["imageUri"],
                        "port": service["containerPort"],
                        "env": service["env"],
                        "num_gpus": service["numGpus"],
                    }
                )
            )
            mapping_render = safe_load(
                mapping_template.render(
                    {
                        "engine_name": service_name,
                    }
                )
            )
            app_api = AppsV1Api(client)
            core_api = CoreV1Api(client)
            try:
                app_api.create_namespaced_deployment(
                    namespace=config.IE_NAMESPACE, body=deployment_render
                )
            except K8sAPIException as err:
                print("Deployment probably already exists")
                print(f"Error: {err}")

            try:
                core_api.create_namespaced_service(
                    namespace=config.IE_NAMESPACE, body=service_render
                )
            except K8sAPIException as err:
                print("Service probably already exists")
                print(f"Error: {err}")

            try:
                custom_api.create_namespaced_custom_object(
                    group="getambassador.io",
                    version="v2",
                    namespace=config.IE_NAMESPACE,
                    plural="mappings",
                    body=mapping_render,
                )
            except K8sAPIException as err:
                print("Mapping probably already exists")
                print(f"Error: {err}")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid service type",
            )
    return {"message": "Service restored", "service": service}


@router.delete("/admin/clear", status_code=status.HTTP_204_NO_CONTENT)
async def wipe_orphaned_services(
    user: TokenData = Depends(get_current_user),
):
    """Call to delete orphaned inference services

    Args:
        user (TokenData, optional): User details and info. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 500 Internal Server Error if there is an error wiping orphaned services
    """
    try:
        if user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have sufficient privilege to clear orphan services!",
            )
        await delete_orphan_services()
        return
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error when trying to wipe orphaned services: {err}",
        )
