from urllib.error import HTTPError

from fastapi import APIRouter, Depends, HTTPException, status
from jinja2 import Template
from kubernetes.client import CustomObjectsApi
from kubernetes.client.rest import ApiException as K8sAPIException
from yaml import safe_load

from ..internal.k8s_client import get_k8s_client
from ..internal.templates import template_env

router = APIRouter(prefix="/engines", tags=["Inference Engines"])


@router.post("/")
async def create_inference_engine(
    model_id: str, image_uri: str, k8s_client=Depends(get_k8s_client)
):
    # First check that model actually exists in DB
    # Create Deployment Template
    template = template_env.get_template("kn-inference-engine.yaml.j2")

    deployment_template = safe_load(
        template.render({"engine_name": model_id, "image_name": image_uri})
    )

    # Deploy Service on K8S
    with k8s_client as client:
        # Create instance of API class
        api = CustomObjectsApi(client)
        try:
            res = await api.create_namespaced_custom_object(
                group="serving.knative.dev",
                version="v1",
                plural="services",
                namespace="IE",
                body=deployment_template,
                async_req=True,
            )
        except (K8sAPIException, HTTPError):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@router.delete("/")
async def delete_inference_engine(
    model_id: str, image_uri: str, k8s_client=Depends(get_k8s_client)
):
    # Delete Service on K8S
    with k8s_client as client:
        # Create instance of API class
        api = CustomObjectsApi(client)
        try:
            res = await api.delete_namespaced_custom_object(
                group="serving.knative.dev",
                version="v1",
                plural="services",
                namespace="IE",
                async_req=True,
            )
        except (K8sAPIException, HTTPError):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@router.patch("/")
async def update_inference_engine(
    model_id: str, image_uri: str, k8s_client=Depends(get_k8s_client)
):
    # Create Deployment Template
    template = template_env.get_template("kn-inference-engine.yaml.j2")

    deployment_template = safe_load(
        template.render({"engine_name": model_id, "image_name": image_uri})
    )

    # Deploy Service on K8S
    with k8s_client as client:
        # Create instance of API class
        api = CustomObjectsApi(client)
        try:
            res = await api.replace_namespaced_custom_object(
                group="serving.knative.dev",
                version="v1",
                plural="services",
                namespace="IE",
                body=deployment_template,
                async_req=True,
            )
        except (K8sAPIException, HTTPError):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
