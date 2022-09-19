import tempfile
import filetype
from os import remove
from pathlib import Path
from shutil import unpack_archive
from typing import Optional

from clearml.datasets import Dataset
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from config.config import config
from internal.file_validator import (
    ValidateFileUpload,
    MaxFileSizeException,
    MaxFileSizeValidator,
    clean_filename,
    determine_safe_file_size,
)

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


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(file_validator)],
)
async def create_dataset(
    file: UploadFile = File(...),
    dataset_name: str = Form(...),
    project_name: str = Form(...),
    output_url: Optional[str] = Form(default=None),
):
    # Check MIME Type. Currently we expect only a compressed file.
    # TODO: check disk usage and size of compressed file to ensure no error. If too large, give appropriate HTTP error
    # TODO: Use add_external_files to allow upload dataset from other locations
    # Write dataset to temp directory
    # NOTE: not using aiofiles for async read and write as performance is slow
    # https://stackoverflow.com/questions/73442335/how-to-upload-a-large-file-%E2%89%A53gb-to-fastapi-backend
    # First determine max file size
    max_file_size = determine_safe_file_size("/", clearance=5)
    file_size_validator = MaxFileSizeValidator(max_size=max_file_size)
    with tempfile.TemporaryDirectory(dataset_name, "clearml-dataset") as dirpath:
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
            "id": dataset.id,
        },
        status_code=status.HTTP_201_CREATED,
    )
