# Helper function to check if Triton is ready
import tritonclient.grpc as grpcclient


def health_check(
    client: grpcclient.InferenceServerClient,
    model_name: str,
    model_version: str = "",
) -> bool:
    """Checks if Triton Server is ready to call inference
    on a model

    :param client: Triton Client
    :type client: grpcclient.InferenceServerClient
    :param model_name: Name of model on the Triton Server
    :type model_name: str
    :param model_version: Version of Triton Model, defaults to ""
    :type model_version: str, optional
    :return: True if server ready, False if not ready
    :rtype: bool
    """
    return (
        client.is_server_live()
        and client.is_server_ready()
        and client.is_model_ready(
            model_name=model_name, model_version=model_version
        )
    )
