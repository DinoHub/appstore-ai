"""AI Appstore Main Module"""
from pathlib import Path
import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles

from .config.config import config
from .internal.auth import check_is_admin, get_current_user
from .internal.tasks import init_db
from .routers import auth, buckets, datasets, engines, experiments, iam, models, exports

with open(
    Path(__file__).parent.parent.joinpath("README.md"), "r", encoding="utf-8"
) as f:
    description = f.read()

tags_metadata = [
    {
        "name": "Models",
        "description": "CRUD endpoints for model cards, as well as for submitting inference.",
    },
    {
        "name": "Experiments",
        "description": "APIs mostly used for the transfer learning feature to make a clone of an existing experiment.",
    },
    {
        "name": "Datasets",
        "description": "APIs mostly used for transfer learning feature to upload dataset used for transfer learning.",
    },
    {
        "name": "Inference Engines",
        "description": "APIs to deploy inference engines",
    },
    {
        "name": "IAM",
        "description": "APIs for system admins to manage users in database in IAM system",
    },
    {
        "name": "Authentication",
        "description": "APIs to allow end users to login to the system",
    },
    {
        "name": "Exports",
        "description": "APIs for system admins to manage export logs",
    },
    {
        "name": "Buckets",
        "description": "APIs to allow for upload and retrieval of media from S3 Storage (MinIO)",
    },
]
fastapi_app = FastAPI(
    title="Model Zoo",
    description=description,
    openapi_tags=tags_metadata,
    on_startup=[init_db],
    docs_url=None,
    redoc_url=None,
)
fastapi_app.mount("/static", StaticFiles(directory="static"), name="static")

logging.getLogger('asyncio').setLevel(logging.CRITICAL)

app = CORSMiddleware(
    fastapi_app,
    allow_origins=[str(origin) for origin in config.FRONTEND_HOST],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=fastapi_app.openapi_url,
        title=fastapi_app.title + " - Swagger UI",
        oauth2_redirect_url=fastapi_app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.app.get(fastapi_app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.app.openapi_url,
        title=fastapi_app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


app.app.include_router(auth.router)
app.app.include_router(buckets.router, dependencies=[Depends(get_current_user)])
app.app.include_router(models.router, dependencies=[Depends(get_current_user)])
app.app.include_router(experiments.router, dependencies=[Depends(get_current_user)])
app.app.include_router(exports.router, dependencies=[Depends(check_is_admin)])
app.app.include_router(datasets.router, dependencies=[Depends(get_current_user)])
app.app.include_router(iam.router, dependencies=[Depends(check_is_admin)])
app.app.include_router(engines.router, dependencies=[Depends(get_current_user)])


@app.app.get("/")
def root():
    """Return a simple message to test if the server is running.

    Returns:
        JSONResponse: A simple message that says "Hello World"
    """
    return {"message": "Hello World"}
