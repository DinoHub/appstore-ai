from kubernetes.client import ApiClient, Configuration
from kubernetes.config import (
    ConfigException,
    load_incluster_config,
    load_kube_config,
)


def get_k8s_client() -> ApiClient:
    k8s_config = Configuration()
    try:
        load_incluster_config(k8s_config)
    except ConfigException:  # app not running within K8S cluster
        from ..config.config import config

        try:
            load_kube_config(client_configuration=k8s_config)
        except ConfigException:
            k8s_config.api_key["authorization"] = config.K8S_API_KEY
            k8s_config.host = config.K8S_HOST
    return ApiClient(k8s_config)
