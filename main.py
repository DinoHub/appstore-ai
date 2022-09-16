from fastapi import FastAPI

from routers import datasets, experiments, models

with open("README.md", "r") as f:
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
]
app = FastAPI(
    title="Model Zoo",
    description=description,
    openapi_tags=tags_metadata
)


app.include_router(models.router)
app.include_router(experiments.router)
app.include_router(datasets.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
