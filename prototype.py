from collections import defaultdict
import tempfile
from enum import Enum
from pathlib import Path
from typing import List, Mapping, Optional, Dict

from clearml import Task, Model
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


class SectionTypes(str, Enum):
    use_case = "Model Use"
    limitations = "Limitations"
    evaluation_metrics = "Evaluation Metrics"
    performance = "Performance"
    explanation = "Explanation"
    deployment = "Deployment"
    license = "License"
    remarks = "Remarks"
    model_config = "Model Format and Framework"


class ModelDescription(BaseModel):
    text: str
    title: str
    media: Optional[Union[List[str], List[Dict]]]


class ModelCard(BaseModel):
    title: str
    description: Dict[SectionTypes, ModelDescription]
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
    return {"id": exp_list.data.id, "name": exp_list.data.name, "rest": exp_list.data}


@app.post("/experiments/clone")
async def clone_exp(item: ClonePackage):
    exp_list = client.tasks.get_by_id(task=item.id)
    if item.clone_name == None:
        new_exp = exp_list.clone(new_task_name=f"Clone of {exp_list.data.name}")
    else:
        new_exp = exp_list.clone(new_task_name=f"{item.clone_name}")
    cloned = client.tasks.get_by_id(task=new_exp.id)
    return {
        "id": exp_list.data.id,
        "name": exp_list.data.name,
        "clone_id": cloned.data.id,
        "clone_name": cloned.data.name,
    }


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
    compressed: bool = Query(
        default=False
    ),  # TODO: Add support for unzipping compressed dataset
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

        dataset = Dataset.create(  # only when writing is finished then create data
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
    # If exp id is provided, some metadata can be obtained from ClearML
    tags = card.tags
    sections = defaultdict(lambda: defaultdict(list), **card.description)
    if card.clearml_exp_id:
        # Retrieve metadata from ClearML experiment
        # Get Scalars if present
        # this data will be passed to front end (Plotly.js)
        # OR we can create plots within here and save the image to db
        # NOTE: I specifically use clearml sdk as it is the only way to get the data points
        # backend rest api does not expose this info (only summary statistics)
        task = Task.get_task(task_id=card.clearml_exp_id)
        plots = task.get_reported_plots()
        sections["Evaluation Metrics"]["media"].extend(
            plots
        )  # do not override existing plots
        # NOTE: switch to backend rest api as only that let's me get info on user
        # NOTE: we can only obtain attributes using "." notation from the data below
        task_data: Mapping[str, Union[str, Mapping]] = client.tasks.get_by_id(
            task=card.clearml_exp_id
        ).data
        # NOTE: I can only get user id, not the name
        # NOTE: consider using userid to form a url to the user account
        user_id = task_data.user

        tags.extend(task_data.tags)
        # Get info on model frameworks
        # Start by getting model id so that we can get them
        # NOTE: client api from testing seems to only give id and name if I use th
        # this is why I don't just use the get_all REST api
        output_models: List[Mapping[str, str]] = task_data.models.output
        # Obtain Id
        # Use set as there can be duplicate model ids as some files refer to same model
        model_ids = set(map(lambda model: model.model, output_models))
        # For each model,
        models = {}
        if model_ids:
            # potentially a script could output multiple models
            for model_id in model_ids:
                model = Model(model_id)
                # NOTE: get_frameworks REST api will give ALL frameworks in project
                # therefore, get them using Model object
                models[model.name] = model.framework
                tags.append(model.framework)
    else:
        # User should have manually filled up info
        pass

    # Finally, push this info into the metacards database
    tags = set(tags)  # remove duplicated tags

    return models, user_id, task_data, plots

    # TODO: If clearml exp id is present, retrieve from clearml
    # GET: Tags, Created By, Framework of Model, Scalars, Pipelines (model performance)

    # Save information into database
