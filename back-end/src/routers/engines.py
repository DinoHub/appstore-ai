from urllib.error import HTTPError
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Path, status
from kubernetes.client import ApiClient, CoreV1Api, CustomObjectsApi
from kubernetes.client.rest import ApiException as K8sAPIException
from kubernetes.client.rest import RESTResponse
from yaml import safe_load

from ..config.config import config
from ..internal.k8s_client import get_k8s_client
from ..internal.templates import template_env
from ..internal.utils import k8s_safe_name
from ..models.engine import InferenceEngineService

router = APIRouter(prefix="/engines", tags=["Inference Engines"])


@router.get("/")
async def get_available_inference_engine_services(
    k8s_client: ApiClient = Depends(get_k8s_client),
):
    try:
        with k8s_client as client:
            api = CustomObjectsApi(client)
            results = api.list_namespaced_custom_object(
                group="knative.serving.dev",
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
    service: InferenceEngineService,
    k8s_client: ApiClient = Depends(get_k8s_client),
):
    """Deploy an Inference Engine as a KNative Service

    :param service: An object containing a service name and an image URI
    :type service: InferenceEngineService
    :param k8s_client: K8S Client, defaults to Depends(get_k8s_client)
    :type k8s_client: ApiClient, optional
    :raises HTTPException: 500 Internal Server Error if K8S deployment fails
    :return: Response from the Python K8S Client
    :rtype: Any # TODO: Find out what the return type is
    """
    # First check that model actually exists in DB
    # Create Deployment Template
    template = template_env.get_template("inference-engine-service.yaml.j2")
    service_name = k8s_safe_name(
        f"{service.owner_id}-{service.model_id}-{uuid4()}"
    )
    deployment_template = safe_load(
        template.render(
            {
                "engine_name": service_name,
                "image_name": service.image_uri,
                "port": service.container_port,
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
        kn_api = CoreV1Api(client)
        kn = kn_api.read_namespaced_service(
            name="kourier", namespace="knative-serving"
        )
        lb_ip = kn.status.load_balancer.ingress[0].ip
        # Create instance of API class
        api = CustomObjectsApi(client)
        try:
            resp = api.create_namespaced_custom_object(
                group="serving.knative.dev",
                version="v1",
                plural="services",
                namespace=config.IE_NAMESPACE,
                body=deployment_template,
            )
        except (K8sAPIException, HTTPError) as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error when creating inference engine: {e}",
            )
        except TypeError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API has no access to the K8S cluster",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error when creating inference engine: {e}",
            )
        return {
            "inference_url": f"{service_name}.{config.IE_NAMESPACE}.{lb_ip}.sslip.io",
            "service_name": service_name,
            "model_id": service.model_id,
            "owner_id": service.owner_id,
        }


@router.delete("/{service_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inference_engine_service(
    service_name: str = Path(description="Name of KService to Delete"),
    k8s_client: ApiClient = Depends(get_k8s_client),
):
    """Delete a deployed inference engine from the K8S cluster.

    :param service_name: Name of KNative service, defaults to Path(description="Name of KService to Delete")
    :type service_name: str, optional
    :param k8s_client: Python K8S Client, defaults to Depends(get_k8s_client)
    :type k8s_client: ApiClient, optional
    :raises HTTPException: 500 Internal Server Error if deletion fails
    """
    # Delete Service on K8S
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


@router.patch("/")
async def update_inference_engine_service(
    service: InferenceEngineService,
    k8s_client: ApiClient = Depends(get_k8s_client),
):
    """Update an existing inference engine inside the K8S cluster

    :param service: Configuration (service name and Image URI) of updated Inference Engine
    :type service: InferenceEngineService
    :param k8s_client: Python K8S client, defaults to Depends(get_k8s_client)
    :type k8s_client: ApiClient, optional
    :raises HTTPException: 500 Internal Server Error if failed to update
    """
    # Create Deployment Template
    template = template_env.get_template("inference-engine-service.yaml.j2")

    deployment_template = safe_load(
        template.render(
            {
                "engine_name": service.service_name,
                "image_name": service.image_uri,
                "image_name": service.container_port,
            }
        )
    )

    # Deploy Service on K8S
    with k8s_client as client:
        # Create instance of API class
        api = CustomObjectsApi(client)
        try:
            api.replace_namespaced_custom_object(
                group="serving.knative.dev",
                version="v1",
                plural="services",
                namespace=config.IE_NAMESPACE,
                name=service.service_name,
                body=deployment_template,
            )
        except (K8sAPIException, HTTPError) as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error when updating inference engine: {e}",
            )
        except TypeError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API has no access to the K8S cluster",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error when updating inference engine: {e}",
            )
