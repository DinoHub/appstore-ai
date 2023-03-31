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
    with k8s_client as client:
        custom_api = CustomObjectsApi(client)
        core_api = CoreV1Api(client)
        apps_api = AppsV1Api(client)

        # Get all services with the label "aas-ie-service"
        if config.IE_SERVICE_TYPE == ServiceBackend.KNATIVE:
            results = custom_api.list_namespaced_custom_object(
                group="serving.knative.dev",
                version="v1",
                plural="services",
                namespace=config.IE_NAMESPACE,
                label_selector="aas-ie-service=true",
            )
            service_names = [
                service["metadata"].name for service in results["items"]
            ]  # NOTE: I don't actually know the response model
            # since the k8s documnentation is not very good
            # and just tells me this will be a dict, but I assume
            # I should be able to access through `items` key
        elif config.IE_SERVICE_TYPE == ServiceBackend.EMISSARY:
            ie_services = core_api.list_namespaced_service(
                namespace=config.IE_NAMESPACE,
                label_selector="aas-ie-service=true",
            ).items
            # Also check for deploymnents and mappings
            ie_deployments = apps_api.list_namespaced_deployment(
                namespace=config.IE_NAMESPACE,
                label_selector="aas-ie-service=true",
            ).items
            ie_mappings = custom_api.list_namespaced_custom_object(
                group="getambassador.io",
                version="v2",
                plural="mappings",
                namespace=config.IE_NAMESPACE,
                label_selector="aas-ie-service=true",
            )["items"]
            service_names = [service.metadata.name for service in ie_services]
            service_names.extend(
                [
                    deployment.metadata.name.removesuffix("-deployment")
                    for deployment in ie_deployments
                ]
            )
            service_names.extend(
                [
                    mapping["metadata"]["name"].removesuffix("-ingress")
                    for mapping in ie_mappings
                ]
            )
        else:
            raise NotImplementedError(
                f"Backend type {config.IE_SERVICE_TYPE} not implemented."
            )
        print(f"Service names: {set(service_names)}")

        # Do a database search for all services that are currently in use
        model_services = await (
            db["models"].find(
                {}, {"inferenceServiceName": 1}
            )  # include only service names
        ).to_list(length=None)
        used_services = [x["inferenceServiceName"] for x in model_services]

        # Do a set difference to find services that are orphaned
        orphaned_services = set(service_names) - set(used_services)
        print(f"INFO: Found {len(orphaned_services)} orphaned services.")
        print(orphaned_services)

        async with await mongo_client.start_session() as session:
            for service_name in orphaned_services:
                # Attempt to find service in database
                service = await db["services"].find_one(
                    {"serviceName": service_name}
                )
                backend_type = config.IE_SERVICE_TYPE
                if service is not None:
                    if "backend" in service:
                        # If backend not present, check config for default
                        backend_type = service["backend"]
                    # Delete service from database
                    async with session.start_transaction():
                        try:
                            await db["services"].delete_one(
                                {"serviceName": service_name}
                            )
                        except Exception as err:
                            print(
                                f"ERROR: Failed to delete service {service_name} from database."
                            )
                            print(err)
                            continue
                # Delete service from cluster
                if backend_type == ServiceBackend.KNATIVE:
                    try:
                        custom_api.delete_namespaced_custom_object(
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
                        else:
                            raise err
                elif backend_type == ServiceBackend.EMISSARY:
                    try:
                        core_api.delete_namespaced_service(
                            name=service_name,
                            namespace=config.IE_NAMESPACE,
                        )
                    except ApiException as err:
                        if err.status == 404:
                            # Service not present
                            print(
                                f"WARN: Service {service_name} not found in cluster."
                            )
                        else:
                            raise err
                    try:
                        apps_api.delete_namespaced_deployment(
                            name=service_name + "-deployment",
                            namespace=config.IE_NAMESPACE,
                        )
                    except ApiException as err:
                        if err.status == 404:
                            # Deployment not present
                            print(
                                f"WARN: Deployment {service_name}-deployment not found in cluster."
                            )
                        else:
                            raise err
                    try:
                        custom_api.delete_namespaced_custom_object(
                            group="getambassador.io",
                            version="v2",
                            plural="mappings",
                            namespace=config.IE_NAMESPACE,
                            name=service_name
                            + "-ingress",  # TODO: make this a separate function so that route can share same code
                        )
                    except ApiException as err:
                        if err.status == 404:
                            # Mapping not present
                            print(
                                f"WARN: Mapping {service_name}-ingress not found in cluster."
                            )
                        else:
                            raise err
                await db["services"].delete_one({"serviceName": service_name})
