from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import datasets, engines, experiments, iam, models

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
        "name": "IAM",
        "description": "APIs for system admins to manage users in database in IAM system",
    },
    {
        "name": "Inference Engines",
        "description": "APIs to deploy inference engines",
    },
]
app = FastAPI(
    title="Model Zoo", description=description, openapi_tags=tags_metadata
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)

app.include_router(models.router)
app.include_router(experiments.router)
app.include_router(datasets.router)
app.include_router(iam.router)
app.include_router(engines.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
