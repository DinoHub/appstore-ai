from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config.config import config
from .internal.auth import check_is_admin, get_current_user
from .routers import auth, buckets, datasets, engines, experiments, iam, models

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
        "name": "Buckets",
        "description": "APIs to allow for upload and retrieval of media from S3 Storage (MinIO)",
    },
]
app = FastAPI(
    title="Model Zoo", description=description, openapi_tags=tags_metadata
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(
        set(
            [
                "http://localhost:9000",
                "http://127.0.0.1:9000",
                "http://172.20.255.203",
                "http://appstore.ai",
                (config.FRONTEND_HOST if config else ""),
            ]
        )
    ),
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_credentials=True,
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Authorization",
        "Access-Control-Allow-Origin",
    ],
)

app.include_router(auth.router)
app.include_router(buckets.router, dependencies=[Depends(get_current_user)])
app.include_router(models.router, dependencies=[Depends(get_current_user)])
app.include_router(
    experiments.router, dependencies=[Depends(get_current_user)]
)
app.include_router(datasets.router, dependencies=[Depends(get_current_user)])
app.include_router(iam.router, dependencies=[Depends(check_is_admin)])
app.include_router(engines.router, dependencies=[Depends(get_current_user)])


@app.get("/")
def root():
    """Return a simple message to test if the server is running.

    Returns:
        JSONResponse: A simple message that says "Hello World"
    """
    return {"message": "Hello World"}
