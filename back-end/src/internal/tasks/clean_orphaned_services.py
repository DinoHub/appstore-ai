"""Task to remove orphaned KNative services."""
from kubernetes.client import CustomObjectsApi
from kubernetes.client.rest import ApiException

from ...config.config import config
from ..dependencies.mongo_client import get_db
from ..dependencies.k8s_client import get_k8s_client


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
                    except ApiException as err:
                        if err.status == 404:
                            # Service not present
                            print(
                                f"WARN: Service {service_name} not found in cluster."
                            )
                            continue
