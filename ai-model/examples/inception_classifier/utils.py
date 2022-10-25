import logging

import tritonclient.grpc as tr


def triton_health_check(
    client: tr.InferenceServerClient, model_name: str, model_version: str = ""
) -> bool:
    """Check for status of Triton Inference Server

    :param client: _description_
    :type client: tr.InferenceServerClient
    :param model_name: _description_
    :type model_name: str
    :param model_version: _description_, defaults to ""
    :type model_version: str, optional
    :return: _description_
    :rtype: bool
    """
    return (
        client.is_server_live()
        and client.is_server_ready()
        and client.is_model_ready(
            model_name=model_name, model_version=model_version
        )
    )


def load_model(
    name: str = "inception_graphdef",
    version: str = "1",
    server_url: str = "127.0.0.1:8001",
    polling: bool = True,
) -> tr.InferenceServerClient:
    """Prepare Triton Client and load in model

    :param name: Name of model in Inference Server, defaults to "inception_graphdef"
    :type name: str, optional
    :param version: Version number of model in Inference Server, defaults to "1"
    :type version: str, optional
    :param server_url: URL to Triton Inference Server, defaults to "127.0.0.1:8001"
    :type server_url: str, optional
    :param pooling: Is Triton Server in POLLING or EXPLICIT mode of loading models
    :type booling, bool, optional
    :raises tr.InferenceServerException: If failed to connect to server or model
    :return: Triton Client
    :rtype: tr.InferenceServerClient
    """
    client = tr.InferenceServerClient(url=server_url)
    logging.info("Successfully connected to Triton Inference Server")
    # Attempt to load model
    if not polling:
        client.load_model(model_name=name)
    # Verify model is ready
    if not triton_health_check(client, name, version):
        logging.error("Connection to model on Triton Server failed")
        raise tr.InferenceServerException
    logging.info("Model loaded and ready for inference")
    return client


def unload_model(
    client: tr.InferenceServerClient,
    model_name: str = "inception_graphdef",
    unload_dependents: bool = True,
) -> None:
    """Unload model from Inference Server

    :param client: Triton Inference Client
    :type client: tr.InferenceServerClient
    :param model_name: Name of model in Inference Server, defaults to "inception_graphdef"
    :type model_name: str, optional
    :param unload_dependents: If dependent models should also be unloaded, defaults to True
    :type unload_dependents: bool, optional
    """
    client.unload_model(
        model_name=model_name, unload_dependents=unload_dependents
    )

    if triton_health_check(client, model_name=model_name):
        logging.error(
            "Failed to unload model or verify status of unloaded model"
        )
