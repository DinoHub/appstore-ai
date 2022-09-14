from clearml.datasets import Dataset
from fastapi import FastAPI
from clearml.backend_api.session.client import APIClient
app = FastAPI()
client = APIClient()
import inspect
from pydantic import BaseModel
from typing import Union

class ClonePackage(BaseModel):
    id: str
    clone_name: Union[str, None] = None

@app.get("/")
async def hello_world():
    return {"message": "hello world"}


@app.get("/experiments/{id}")
async def get_experiment(id: str):
    exp_list = client.tasks.get_by_id(task=id)
    return {"id": exp_list.data.id, "name" : exp_list.data.name}
    
@app.post("/experiments/clone")
async def clone_exp(item: ClonePackage):
    exp_list = client.tasks.get_by_id(task=item.id)
    if item.clone_name == None:
        new_exp = exp_list.clone(new_task_name = f'Clone of {exp_list.data.name}')
    else: 
        new_exp = exp_list.clone(new_task_name = f'{item.clone_name}')
    cloned = client.tasks.get_by_id(task=new_exp.id)
    return {"id": exp_list.data.id, "name" : exp_list.data.name,"clone_id": cloned.data.id,"clone_name":cloned.data.name}

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
