from urllib.error import HTTPError

from fastapi import APIRouter, Depends, HTTPException, Path, status
from kubernetes.client import CustomObjectsApi
from kubernetes.client.rest import ApiException as K8sAPIException
from yaml import safe_load

from ..config.config import config
from ..internal.k8s_client import get_k8s_client
from ..internal.templates import template_env
from ..models.engine import InferenceEngineService

router = APIRouter(prefix="/engines", tags=["Inference Engines"])


@router.post("/")
async def create_inference_engine_service(
    service: InferenceEngineService,
    k8s_client=Depends(get_k8s_client),
):
    # First check that model actually exists in DB
    # Create Deployment Template
    template = template_env.get_template("inference-engine-service.yaml.j2")

    deployment_template = safe_load(
        template.render(
            {
                "engine_name": service.service_name,
                "image_name": service.image_uri,
            }
        )
    )

    # Deploy Service on K8S
    with k8s_client as client:
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
        return resp


@router.delete("/{service_name}")
async def delete_inference_engine_service(
    service_name: str = Path(description="Name of KService to Delete"),
    k8s_client=Depends(get_k8s_client),
):
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


@router.patch("/")
async def update_inference_engine_service(
    service: InferenceEngineService,
    k8s_client=Depends(get_k8s_client),
):
    # Create Deployment Template
    template = template_env.get_template("inference-engine-service.yaml.j2")

    deployment_template = safe_load(
        template.render(
            {
                "engine_name": service.service_name,
                "image_name": service.image_uri,
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
