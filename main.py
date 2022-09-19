from fastapi import FastAPI

from routers import datasets, experiments, models,iam

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
    {
        "name": "IAM",
        "description": "APIs for system admins to manage users in database in IAM system",
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
app.include_router(iam.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import click
    import uvicorn
    @click.command()
    @click.option("--host", default="0.0.0.0")
    @click.option("--port", default=8080)
    @click.option("--reload", is_flag=True)
    def main(host, port, reload):
        uvicorn.run(app, host=host, port=port, reload=reload)
    main()