import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Union
from uuid import uuid4

from fastapi import File, Request, UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile

CHUNK_SIZE = 4096


async def process_inference_data(
    request: Request,
) -> Tuple[Dict[str, List[str]], Dict[str, Union[str, Dict]]]:
    files = defaultdict(list)
    texts = {}
    form = await request.form()
    for fieldname, value in form.items():
        if isinstance(value, StarletteUploadFile):
            # need to use Starlette UploadFile as it will not be
            # recognized otherwise
            files[fieldname].append(download_file(value))
        else:
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
            texts[fieldname] = value
    return files, texts


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


def remove_unused_files(files: Dict[str, List[str]]) -> None:
    """Cleanup function to remove leftover files made
    during a request. This prevents the container from
    being clogged up with old files.

    :param files: A dictionary containing fields as key, values as list of file paths
    :type files: Dict[str, List[str]]
    """
    if files is None:
        return
    for field_files in files.values():
        for file_path in field_files:
            file_path = Path(file_path).unlink(missing_ok=True)
