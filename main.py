from fastapi import FastAPI

from routers import datasets, experiments, models,users

app = FastAPI()

app.include_router(models.router)
app.include_router(experiments.router)
app.include_router(datasets.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {
        "message" : "Hello World"
    }