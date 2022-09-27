import tempfile
from os import remove
from pathlib import Path
from shutil import unpack_archive
from typing import List, Optional

import filetype
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.exceptions import HTTPException

from ..config.config import config
from ..internal.data_connector import Dataset
from ..internal.file_validator import (
    MaxFileSizeException,
    MaxFileSizeValidator,
    ValidateFileUpload,
    clean_filename,
    determine_safe_file_size,
)
from ..models.dataset import DatasetModel, FindDatasetModel

DATA_CONNECTOR = "clearml"
ACCEPTED_CONTENT_TYPES = [
    "application/zip",
    "application/x-tar",
    "application/gzip",
    "application/x-bzip2",
]
CHUNK_SIZE = 1024
BytesPerGB = 1024 * 1024 * 1024
MAX_UPLOAD_SIZE_GB = config.MAX_UPLOAD_SIZE_GB
file_validator = ValidateFileUpload(
    max_upload_size=MAX_UPLOAD_SIZE_GB
    if MAX_UPLOAD_SIZE_GB is None
    else BytesPerGB * MAX_UPLOAD_SIZE_GB,
)  # Note, cannot validate file type here as content-type will be multipart form upload
router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.post(
    "/search",
    response_model=List[DatasetModel],
    response_model_exclude=["files", "default_remote"],
)
async def search_datasets(query: FindDatasetModel):
    datasets = Dataset(connector_type=DATA_CONNECTOR).list_datasets(
        project=query.project,
        partial_name=query.name,
        tags=query.tags,
        ids=query.id,
    )
    return datasets


@router.get("/{dataset_id}", response_model=DatasetModel)
async def get_dataset_by_id(dataset_id: str):
    try:
        dataset = Dataset(connector_type=DATA_CONNECTOR).get(id=dataset_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with ID {dataset_id} not found.",
        )
    return DatasetModel(
        id=dataset.id,
        name=dataset.name,
        project=dataset.project,
        tags=dataset.tags,
        files=dataset.file_entries,
        default_remote=dataset.default_remote,
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(file_validator)],
    response_model=DatasetModel,
)
async def create_dataset(
    file: UploadFile = File(...),
    dataset_name: str = Form(...),
    project_name: str = Form(...),
    output_url: Optional[str] = Form(default=None),
):
    # Write dataset to temp directory
    # NOTE: not using aiofiles for async read and write as performance is slow
    # https://stackoverflow.com/questions/73442335/how-to-upload-a-large-file-%E2%89%A53gb-to-fastapi-backend
    # First determine max file size
    max_file_size = determine_safe_file_size("/", clearance=5)
    file_size_validator = MaxFileSizeValidator(max_size=max_file_size)
    # TODO: Refactor code to make it more readable
    with tempfile.TemporaryDirectory(
        dataset_name, "clearml-dataset"
    ) as dirpath:
        # write file to fs
        try:
            path = Path(dirpath, clean_filename(file.filename))
            # First get file size
            with open(path, "wb") as f:
                while content := file.file.read(
                    CHUNK_SIZE
                ):  # Read in chunks to avoid memory issues
                    file_size_validator(
                        content
                    )  # checks total file size of all files uploaded
                    f.write(content)
            # Validate File type
            content_type = filetype.guess_mime(path)
            if content_type not in ACCEPTED_CONTENT_TYPES:
                raise ValueError
        except MaxFileSizeException:
            remove(path)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Dataset uploaded was too large for the server to handle.",
            )
        except ValueError:
            remove(path)
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type of compressed file {file.filename} is not supported.",
            )
        except Exception:
            remove(path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="There was an error reading the file",
            )
        try:
            unpack_archive(filename=path, extract_dir=dirpath)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type of compressed file {file.filename} is not supported.",
            )
        except Exception:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error when decompressing dataset",
            )
        finally:
            # this will still run even if HTTPException is raised
            remove(path)  # remove zipfile so it is not uploaded
        dataset = Dataset(connector_type=DATA_CONNECTOR).create(
            name=dataset_name,
            project=project_name,
        )
        # then, add entire dir
        dataset.add_files(dirpath)
        # upload
        # NOTE: this process takes quite long
        # TODO: see if I can make this non-blocking
        dataset.upload(remote=output_url)
    return DatasetModel(
        id=dataset.id,
        name=dataset.name,
        tags=dataset.tags,
        project=dataset.project,
        files=dataset.file_entries,
    )
