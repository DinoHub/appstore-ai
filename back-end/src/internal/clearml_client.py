from pathlib import Path
from typing import Optional, Union

from clearml.backend_api.session.client import APIClient, StrictSession

from ..config.config import config


def clearml_api_client(
    config_path: Optional[Union[str, Path]] = None
) -> APIClient:
    if not config_path:
        config_path = config.CLEARML_CONFIG_FILE
    session = StrictSession(config_file=config_path)
    client = APIClient(session=session)
    return client
