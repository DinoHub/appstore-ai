from kubernetes.client import ApiClient, Configuration
from kubernetes.config import ConfigException, load_incluster_config


def get_k8s_client() -> ApiClient:
    k8s_config = Configuration()
    try:
        load_incluster_config(k8s_config)
    except ConfigException:
        from ..config.config import config

        k8s_config.api_key["authorization"] = config.K8S_API_KEY
        k8s_config.host = config.K8S_API_KEY
    return ApiClient(k8s_config)
