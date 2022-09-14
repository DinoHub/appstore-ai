import tempfile
from enum import Enum
from pathlib import Path
from typing import List, Optional

from clearml import Task
from clearml.backend_api.session.client import APIClient
from clearml.datasets import Dataset
from fastapi import FastAPI, File, Query, UploadFile
from pydantic import BaseModel

app = FastAPI()
client = APIClient()
from typing import Union

from pydantic import BaseModel


class SecurityClassification(str, Enum):
    unclassified = "unclassified"
class ModelDescription(BaseModel):
    text: str
    title: str
    media: Optional[List[str]]
class ModelCard(BaseModel):
    title: str
    description: List[ModelDescription]
    datetime: str
    tags: List[str]
    security_classification: SecurityClassification
    owner: str
    creator: Optional[str]
    # TODO: Figure out model source stuff
    clearml_exp_id: Optional[str]
    inference_url: str
    output_generator_url: str



class ClonePackage(BaseModel):
    id: str
    clone_name: Union[str, None] = None

@app.get("/")
async def hello_world():
    return {"message": "hello world"}


@app.get("/experiments/{id}")
async def get_experiment(id: str):
    exp_list = client.tasks.get_by_id(task=id)
    return {"id": exp_list.data.id, "name" : exp_list.data.name, "rest" : exp_list.data}
    
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


@app.post("/datasets/{project_name}/{dataset_name}")
async def create_dataset(
    project_name: str,
    dataset_name: str,
    files: List[UploadFile] = File(description="Dataset files"),
    compressed: bool = Query(default=False) # TODO: Add support for unzipping compressed dataset
):
    """Given a set of files, upload them to ClearML Data as a Dataset

    Args:
        project_name (str): Name of ClearML project
        dataset_name (str): Name of dataset
        files (List[UploadFile]): Files in dataset to be uploaded (multipart-form)
    """
    # TODO: Use add_external_files to allow upload dataset from other locations
    # Write dataset to temp directory
    # NOTE: not using aiofiles for async read and write as performance is slow
    with tempfile.TemporaryDirectory(dataset_name, "clearml-dataset") as dirpath:
        for file in files:
            # write file to fs
            with open(Path(dirpath, file.filename), "wb") as f:
                while content := file.file.read(1024):  # Read in chunks
                    f.write(content)
        
        dataset = Dataset.create( # only when writing is finished then create data
            dataset_name=dataset_name, dataset_project=project_name
        )
        # then, add entire dir
        dataset.add_files(dirpath, verbose=True)  # TODO: Set to False in prod
        # upload
        dataset.upload(
            show_progress=True
        )  # TODO: allow upload files to other locations

        dataset.finalize(verbose=True)
        return dataset.id, dataset.file_entries_dict

@app.get("/models")
async def get_all_model_cards():
    raise NotImplementedError

@app.post("/models/")
async def create_model_card(card: ModelCard):
    print(card.dict())
    # TODO: Check if clearml exp id is present
    if card.clearml_exp_id:
        task = Task.get_task(
            task_id=card.clearml_exp_id
        )
        # Retrieve metadata from ClearML experiment
        # Get Scalars if present
        scalar_data = task.get_reported_plots()

        # get other metadata
        tags = task.get_tags()



    # TODO: If clearml exp id is present, retrieve from clearml
    # GET: Tags, Created By, Framework of Model, Scalars, Pipelines (model performance)

    # Save information into database
    
