import tempfile
from os import remove
from pathlib import Path
from shutil import unpack_archive
from typing import List, Optional

from clearml.datasets import Dataset
from fastapi import APIRouter, File, Form, Query, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

router = APIRouter(prefix="/datasets")


@router.get("/")
async def get_all_datasets():
    datasets = Dataset.list_datasets()
    return datasets


@router.get("/projects/{project_name}")
async def get_datasets_by_project(project_name: str):
    # TODO: Check that project exists, else return 404
    datasets = Dataset.list_datasets(partial_name=project_name)
    return datasets


@router.get("/{dataset_id}")
async def get_dataset_by_id(dataset_id: str):
    try:
        dataset = Dataset.get(dataset_id=dataset_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with ID {dataset_id} not found.",
        )
    return dataset.file_entries_dict


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_dataset(
    project_name: str = Form(),
    dataset_name: str = Form(),
    files: List[UploadFile] = File(description="Dataset files"),
    output_url: Optional[str] = Form(default=None),
    compressed: bool = Query(default=False),
):
    # TODO: Use add_external_files to allow upload dataset from other locations
    # Write dataset to temp directory
    # NOTE: not using aiofiles for async read and write as performance is slow
    with tempfile.TemporaryDirectory(dataset_name, "clearml-dataset") as dirpath:
        for file in files:
            # write file to fs
            path = Path(dirpath, file.filename)
            with open(path, "wb") as f:
                while content := file.file.read(1024):  # Read in chunks
                    f.write(content)
            if compressed:  # unzip
                try:
                    unpack_archive(filename=path, extract_dir=dirpath)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"File type of compressed file {file.filename} is not supported.",
                    )
                finally:
                    # this will still run even if HTTPException is raised
                    remove(path)  # remove zipfile so it is not uploaded

        dataset = Dataset.create(  # only when writing is finished then create data
            dataset_name=dataset_name, dataset_project=project_name
        )
        # then, add entire dir
        dataset.add_files(dirpath, verbose=True)  # TODO: Set to False in prod
        # upload
        # NOTE: this process takes quite long
        # TODO: see if I can make this non-blocking
        dataset.upload(show_progress=True, output_url=output_url)

        dataset.finalize(verbose=True)

        return JSONResponse(
            content={
                "id" : dataset.id,
            }, status_code=status.HTTP_201_CREATED
        )
