from typing import Optional

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


def get_model_config(
    client: tr.InferenceServerClient, name: str, version: str = ""
):
    # TODO: Get model config dynamically so dev does not need to specify
    model_config: dict = client.get_model_config(name, version, as_json=True)
    raise NotImplementedError


def get_client(
    url: str,
    ssl: bool = False,
    root_certificates: Optional[str] = None,
    private_key: Optional[str] = None,
    certificate_chain: Optional[str] = None,
    **kwargs
) -> tr.InferenceServerClient:
    client = tr.InferenceServerClient(
        url=url,
        ssl=ssl,
        root_certificates=root_certificates,
        private_key=private_key,
        certificate_chain=certificate_chain,
        **kwargs
    )
    return client


def load_model(
    client: tr.InferenceServerClient,
    name: str,
    version: str,
    polling: bool = True,
):
    if not polling:
        client.load_model(model_name=name)
    if not triton_health_check(client, name, version):
        raise tr.InferenceServerException(
            msg="Triton not ready! Health check failed."
        )


def unload_model(
    client: tr.InferenceServerClient,
    name: str,
    unload_dependents: bool = False,
):
    client.unload_model(model_name=name, unload_dependents=unload_dependents)
