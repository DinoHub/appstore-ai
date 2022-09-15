import tempfile
from pathlib import Path
from typing import List

from clearml.datasets import Dataset
from fastapi import APIRouter, File, Query, UploadFile

router = APIRouter(prefix="/datasets")


@router.get("/")
async def get_all_datasets():
    datasets = Dataset.list_datasets()
    return datasets


@router.get("/projects/{project_name}")
async def get_datasets_by_project(project_name: str):
    datasets = Dataset.list_datasets(partial_name=project_name)
    return datasets


@router.get("/{dataset_id}")
async def get_dataset_by_id(dataset_id: str):
    dataset = Dataset.get(dataset_id=dataset_id)
    return dataset.file_entries_dict


@router.post("/{project_name}/{dataset_name}")
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
