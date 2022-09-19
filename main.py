from fastapi import FastAPI

from routers import datasets, experiments, models

app = FastAPI()

app.include_router(models.router)
app.include_router(experiments.router)
app.include_router(datasets.router)

@app.get("/")
async def root():
    return {
        "message" : "Hello World"
    }