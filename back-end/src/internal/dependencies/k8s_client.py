"""Create a K8S client for use in the app."""
from kubernetes.client import ApiClient, Configuration
from kubernetes.config import ConfigException, load_incluster_config, load_kube_config

from ...config.config import config


def get_k8s_client() -> ApiClient:
    """Create a K8S client to interact with the cluster.

    Returns:
        ApiClient: K8S client
    """
    k8s_config = Configuration()
    try:
        load_incluster_config(k8s_config)
    except ConfigException:  # app not running within K8S cluster

        try:
            load_kube_config(client_configuration=k8s_config)
        except ConfigException:
            k8s_config.api_key["authorization"] = config.K8S_API_KEY
            k8s_config.host = config.K8S_HOST
    return ApiClient(k8s_config)
