import tritonclient.grpc as tr


def triton_health_check(
    client: tr.InferenceServerClient, model_name: str, model_version: str
) -> bool:
    """Checks the status of the Triton Inference Server and
    the model

    :param client: Triton Client
    :type client: tr.InferenceServerClient
    :param model_name: Name of the model
    :type model_name: str
    :param model_version: Version of the model (e.g "1")
    :type model_version: str, optional
    :return: If everything is up, return True
    :rtype: bool
    """
    return (
        client.is_server_live()
        and client.is_server_ready
        and client.is_model_ready(
            model_name=model_name, model_version=model_version
        )
    )


def load_model(
    name: str,
    version: str,
    triton_url: str,
    polling: bool = True,
) -> tr.InferenceServerClient:
    client = tr.InferenceServerClient(url=triton_url)
    if not polling:
        client.load_model(model_name=name)
    if not triton_health_check(client, name, version):
        raise tr.InferenceServerException(
            msg="Triton not ready! Health check failed."
        )
    return client


def unload_model(
    client: tr.InferenceServerClient,
    name: str,
    unload_dependents: bool = False,
):
    client.unload_model(model_name=name, unload_dependents=unload_dependents)
