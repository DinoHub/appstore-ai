"""Endpoint to handle datasets"""
import tempfile
from datetime import datetime
from os import remove
from pathlib import Path
from shutil import unpack_archive
from typing import Dict, List, Optional

import filetype
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.exceptions import HTTPException

from ..config.config import config
from ..internal.data_connector import Dataset
from ..internal.dependencies.file_validator import (
    MaxFileSizeException,
    MaxFileSizeValidator,
    ValidateFileUpload,
    clean_filename,
    determine_safe_file_size,
)
from ..models.dataset import Connector, DatasetModel, FindDatasetModel

ACCEPTED_CONTENT_TYPES = [
    "application/zip",
    "application/x-tar",
    "application/gzip",
    "application/x-bzip2",
]
CHUNK_SIZE = 1024
BYTES_PER_GB = 1024 * 1024 * 1024
MAX_UPLOAD_SIZE_GB = config.MAX_UPLOAD_SIZE_GB
file_validator = ValidateFileUpload(
    max_upload_size=None
    if MAX_UPLOAD_SIZE_GB is None
    else int(BYTES_PER_GB * MAX_UPLOAD_SIZE_GB),
)  # Note, cannot validate file type here as content-type will be multipart form upload
router = APIRouter(prefix="/datasets", tags=["Datasets"])


# TODO: Convert to GET request
@router.post(
    "/search",
    response_model=List[DatasetModel],
    response_model_exclude={"files", "default_remote"},
)
def search_datasets(
    query: FindDatasetModel,
    connectors: Optional[List[Connector]] = Query(
        default=None, alias="connectors[]"
    ),
) -> List[Dict]:
    """Search endpoint for any datasets stored in
    the current data connector

    Args:
        query (FindDatasetModel): Search query
        connectors (Optional[List[Connector]]): Data connector.
            If not specified

    Returns:
        List[Dict]: List of dataset metadata
    """
    datasets = []
    if connectors is None:
        connectors = [
            connector.value for connector in Connector if connector.value != ""
        ]
    for connector in connectors:
        datasets.extend(
            Dataset.from_connector(connector).list_datasets(
                project=query.project,
                partial_name=query.name,
                tags=query.tags,
                ids=query.id,
            )
        )
    return datasets


@router.get("/{dataset_id}", response_model=DatasetModel)
async def get_dataset_by_id(
    dataset_id: str, connector: Connector = Query(...)
) -> DatasetModel:
    """Get a dataset from it's ID

    Args:
        dataset_id (str): ID of dataset (e.g ClearML Dataset ID)
        connector (Connector): Data connector type

    Raises:
        HTTPException: 404 Not Found if dataset not found

    Returns:
        DatasetModel: Dataset with that ID
    """
    try:
        dataset = Dataset.from_connector(connector).get(id=dataset_id)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with ID {dataset_id} not found.",
        ) from err
    return DatasetModel(
        id=dataset_id,
        name=dataset.name,
        project=dataset.project,
        tags=dataset.tags,
        files=dataset.file_entries,
        default_remote=dataset.default_remote,
        created=None,
        artifacts=dataset.artifacts,
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
    connector: Connector = Form(...),
    output_url: Optional[str] = Form(default=None),
) -> DatasetModel:
    """Create a new dataset, based on a dataset file uploaded to it

    Args:
        file (UploadFile, optional): Archived dataset (e.g zip). Defaults to File(...).
        dataset_name (str, optional): Name of dataset. Defaults to Form(...).
        project_name (str, optional): Name of project to uplaod to. Defaults to Form(...).
        connector(Connector): Data connector to use.
        output_url (Optional[str], optional): Remote URL to upload file to. Defaults to Form(default=None).

    Raises:
        HTTPException: 413 Request Entity Too Large if dataset size is too large
        HTTPException: 415 Unsupported Media Type if wrong file type
        HTTPException: 500 Internal Server Error if any IOErrors

    Returns:
        DatasetModel : Created dataset
    """
    # Write dataset to temp directory
    # NOTE: not using aiofiles for async read and write as performance is slow
    # https://stackoverflow.com/questions/73442335/how-to-upload-a-large-file-%E2%89%A53gb-to-fastapi-backend
    # First determine max file size
    max_file_size = determine_safe_file_size("/", clearance=5)
    file_size_validator = MaxFileSizeValidator(max_size=max_file_size)
    path = None
    # TODO: Refactor code to make it more readable
    with tempfile.TemporaryDirectory(prefix="dataset-") as dirpath:
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
        except MaxFileSizeException as err:
            if path:
                remove(path)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Dataset uploaded was too large for the server to handle.",
            ) from err
        except ValueError as err:
            if path:
                remove(path)
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type of compressed file {file.filename} is not supported.",
            ) from err
        except Exception as err:
            if path:
                remove(path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="There was an error reading the file",
            ) from err
        try:
            unpack_archive(filename=path, extract_dir=dirpath)
        except ValueError as err:  # Redundant?
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type of compressed file {file.filename} is not supported.",
            ) from err
        except Exception as err:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error when decompressing dataset",
            ) from err
        finally:
            # this will still run even if HTTPException is raised
            remove(path)  # remove zipfile so it is not uploaded
        dataset = Dataset.from_connector(connector).create(
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
        default_remote=dataset.default_remote,
        created=datetime.now(),
    )
