import tempfile
from os import remove
from pathlib import Path
from shutil import unpack_archive, disk_usage
from typing import List, Optional
from urllib.request import Request

from clearml.datasets import Dataset
from fastapi import APIRouter, File, Form, Query, UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from internal.file_validator import MaxFileSizeException, MaxFileSizeValidator


router = APIRouter(prefix="/datasets", tags=["Datasets"])


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


# @router.post("/", status_code=status.HTTP_201_CREATED)
# async def create_dataset(
#   request: Request 
# ):
#     # TODO: check disk usage and size of compressed file to ensure no error. If too large, give appropriate HTTP error
#     # TODO: Use add_external_files to allow upload dataset from other locations
#     # Write dataset to temp directory
#     # NOTE: not using aiofiles for async read and write as performance is slow
#     # https://stackoverflow.com/questions/73442335/how-to-upload-a-large-file-%E2%89%A53gb-to-fastapi-backend
#     # First determine max file size
#     max_file_size = determine_safe_file_size() # TODO
#     fs_validator = MaxFileSizeValidator() 
#     with tempfile.TemporaryDirectory(dataset_name, "clearml-dataset") as dirpath:
#         # write file to fs
#         path = Path(dirpath, file.filename)
#         with open(path, "wb") as f:
#             # First, get file size
#             file_size = len(file.read())
#             while content := file.file.read(1024):  # Read in chunks
#                 f.write(content)
#         try:
#             unpack_archive(filename=path, extract_dir=dirpath)
#         except ValueError:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"File type of compressed file {file.filename} is not supported.",
#             )
#         finally:
#             # this will still run even if HTTPException is raised
#             remove(path)  # remove zipfile so it is not uploaded

#     dataset = Dataset.create(  # only when writing is finished then create data
#         dataset_name=dataset_name, dataset_project=project_name
#     )
#     # then, add entire dir
#     dataset.add_files(dirpath, verbose=True)  # TODO: Set to False in prod
#     # upload
#     # NOTE: this process takes quite long
#     # TODO: see if I can make this non-blocking
#     dataset.upload(show_progress=True, output_url=output_url)

#     dataset.finalize(verbose=True)

#     return JSONResponse(
#         content={
#             "id": dataset.id,
#         },
#         status_code=status.HTTP_201_CREATED,
#     )
