import tritonclient.grpc as tr


def triton_health_check(
    client: tr.InferenceServerClient, model_name: str, model_version: str = ""
):
    return (
        client.is_server_live()
        and client.is_server_ready
        and client.is_model_ready(
            model_name=model_name, model_version=model_version
        )
    )


def load_model(
    name: str = "xlm_roberta_zsl",
    version: str = "1",
    triton_url: str = "172.20.0.4:8001",
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
    name: str = "xlm_roberta_zsl",
    unload_dependents: bool = True,
):
    client.unload_model(model_name=name, unload_dependents=unload_dependents)
