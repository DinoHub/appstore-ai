from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Union
from uuid import uuid4

from fastapi import File, UploadFile

CHUNK_SIZE = 4096


def download_file(file: UploadFile = File()) -> str:
    """Download file that has been sent by the request.

    We generate a unique filename for each file, that still contains
    the original filename. This is useful in cases where,
    the filename contains information (e.g a category, formfield).

    :param file: File to be written locally, defaults to File()
    :type file: UploadFile, optional
    :return: File path to the downloaded file
    :rtype: str
    """
    # Generate a filename
    filename, ext = file.filename.rsplit(".", maxsplit=1)
    unique_filename = f"{str(uuid4())}-{filename}.{ext}"
    with open(unique_filename, "w") as f:
        while content := file.file.read(CHUNK_SIZE):
            f.write(content)
    return unique_filename


def remove_unused_files(files: Union[List[str], str]) -> None:
    """Cleanup function to remove leftover files made
    during a request. This prevents the container from
    being clogged up with old files.

    :param files: A file path or list of file paths
    :type files: Union[List[str], str]
    """
    if files is None:
        return
    if type(files) is str:
        files = [files]
    for file_path in files:
        file_path = Path(file_path).unlink(missing_ok=True)
