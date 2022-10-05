import os

from clearml.backend_api.session.client import APIClient

from ..config.config import clear_conf

try:
    os.environ["CLEARML_WEB_HOST"] = clear_conf.CLEARML_WEB_HOST
    os.environ["CLEARML_API_HOST"] = clear_conf.CLEARML_API_HOST
    os.environ["CLEARML_FILES_HOST"] = clear_conf.CLEARML_FILES_HOST
    os.environ["CLEARML_API_ACCESS_KEY"] = clear_conf.CLEARML_API_ACCESS_KEY
    os.environ["CLEARML_API_SECRET_KEY"] = clear_conf.CLEARML_API_SECRET_KEY
    print('ClearML ENV vars set')
except TypeError as e:
    print(
        "Warning: Failed to set ClearML envvars. It will rely on your local configuration"
    )

clearml_client = APIClient()
