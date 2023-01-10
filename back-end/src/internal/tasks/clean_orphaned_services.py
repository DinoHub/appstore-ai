"""Task to remove orphaned KNative services."""
from kubernetes.client import AppsV1Api, CoreV1Api, CustomObjectsApi
from kubernetes.client.rest import ApiException

from ...config.config import config
from ...models.engine import ServiceBackend
from ..dependencies.k8s_client import get_k8s_client
from ..dependencies.mongo_client import get_db


async def delete_orphan_services():
    """Delete any services that are not referenced in any model card."""
    print("INFO: Starting task to remove orphaned services")
    db, mongo_client = get_db()
    k8s_client = get_k8s_client()

    model_services = await (
        db["models"].find(
            {}, {"inferenceServiceName": 1}
        )  # include only service names
    ).to_list(length=None)
    # Do a search of all services NOT IN modelServices
    # This should detect any services that are not referenced in any model card
    # all new services have uuid in the service name, so this should be safe
    orphaned_services = db["services"].find(
        {
            "serviceName": {
                "$nin": [x["inferenceServiceName"] for x in model_services]
            }
        },
        {"serviceName": 1},
    )
    with k8s_client as client:
        custom_api = CustomObjectsApi(client)
        core_api = CoreV1Api(client)
        apps_api = AppsV1Api(client)
        async with await mongo_client.start_session() as session:
            async for service in orphaned_services:
                # Remove service
                service_name = service["serviceName"]
                backend_type = service["backend"]
                async with session.start_transaction():
                    try:
                        await db["services"].delete_one(
                            {"serviceName": service_name}
                        )
                        if backend_type == ServiceBackend.knative:
                            custom_api.delete_namespaced_custom_object(
                                group="serving.knative.dev",
                                version="v1",
                                plural="services",
                                namespace=config.IE_NAMESPACE,
                                name=service_name,
                            )
                        elif backend_type == ServiceBackend.emissary:
                            core_api.delete_namespaced_service(
                                name=service_name,
                                namespace=config.IE_NAMESPACE,
                            )
                            apps_api.delete_namespaced_deployment(
                                name=service_name + "-deployment",
                                namespace=config.IE_NAMESPACE,
                            )
                            custom_api.delete_namespaced_custom_object(
                                group="getambassador.io",
                                version="v2",
                                plural="mappings",
                                namespace=config.IE_NAMESPACE,
                                name=service_name
                                + "-mapping",  # TODO: make this a separate function so that route can share same code
                            )
                    except ApiException as err:
                        if err.status == 404:
                            # Service not present
                            print(
                                f"WARN: Service {service_name} not found in cluster."
                            )
                            continue
