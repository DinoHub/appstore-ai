from clearml.datasets import Dataset
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def hello_world():
    return {"message": "hello world"}


@app.get("/datasets")
async def get_all_datasets():
    datasets = Dataset.list_datasets()
    return datasets


@app.get("/datasets/projects/{project_name}")
async def get_datasets_by_project(project_name: str):
    datasets = Dataset.list_datasets(partial_name=project_name)
    return datasets


@app.get("/datasets/{dataset_id}")
async def get_dataset_by_id(dataset_id: str):
    dataset = Dataset.get(dataset_id=dataset_id)
    return dataset.file_entries_dict
