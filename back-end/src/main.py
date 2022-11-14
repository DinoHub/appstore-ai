from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .internal.auth import check_is_admin, get_current_user
from .routers import auth, datasets, engines, experiments, iam, models

with open(Path(__file__).parent.parent.joinpath("README.md"), "r") as f:
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
]
app = FastAPI(
    title="Model Zoo", description=description, openapi_tags=tags_metadata
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Replace with config file?
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(models.router, dependencies=[Depends(get_current_user)])
app.include_router(
    experiments.router, dependencies=[Depends(get_current_user)]
)
app.include_router(datasets.router, dependencies=[Depends(get_current_user)])
app.include_router(iam.router, dependencies=[Depends(check_is_admin)])
app.include_router(engines.router, dependencies=[Depends(get_current_user)])


@app.get("/")
async def root():
    return {"message": "Hello World"}
