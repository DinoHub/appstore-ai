from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Union

from fastapi import File, UploadFile

CHUNK_SIZE = 4096


def download_file(file: UploadFile = File()) -> str:
    """Download file that has been sent by the request.

    :param file: File to be written locally, defaults to File()
    :type file: UploadFile, optional
    :return: File path to the downloaded file
    :rtype: str
    """
    with NamedTemporaryFile(delete=False) as f:
        filename = f.name
        while content := file.file.read(CHUNK_SIZE):
            f.write(content)
    return filename


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
