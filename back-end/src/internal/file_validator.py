import string
import unicodedata
from shutil import disk_usage
from typing import List, Optional, Union

from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.requests import Request

# https://gist.github.com/wassname/1393c4a57cfcbf03641dbc31886123b8
VALID_FILENAME_CHARS = f"-_.() {string.ascii_letters}{string.digits}"
CHAR_LIMIT = 255


class MaxFileSizeException(Exception):
    def __init__(self, fs: int):
        self.fs = fs


class MaxFileSizeValidator:
    def __init__(self, max_size: int):
        self.fs = 0
        self.max_size = max_size

    def __call__(self, chunk: bytes):
        self.fs += len(chunk)
        if self.fs > self.max_size:
            raise MaxFileSizeException(fs=self.fs)


def determine_safe_file_size(
    path: str = "/", clearance: Union[int, float] = 5
) -> int:
    # clearance is because we need to give space for decompression
    assert clearance > 0
    (_, _, free) = disk_usage(path)
    # we only need the free disk usage
    # let clearance=5
    # safe size = (5*file_size) < free
    # safe size = (file size) < free / 5
    return int(free / clearance)


def clean_filename(
    filename: str, whitelist: str = VALID_FILENAME_CHARS, replace: str = " "
) -> str:
    """
    Clean filename to ensure it is safe for filesystem

    Taken from: https://gist.github.com/wassname/1393c4a57cfcbf03641dbc31886123b8

    Args:
        filename (str): Filename
        whitelist (str, optional): Chars to ignore. Defaults to VALID_FILENAME_CHARS.
        replace (str, optional): What to replace invalid chars with. Defaults to " ".

    Returns:
        str: Cleaned URL.
    """
    # replace spaces
    for r in replace:
        filename = filename.replace(r, "_")

    # keep only valid ascii chars
    cleaned_filename = (
        unicodedata.normalize("NFKD", filename)
        .encode("ASCII", "ignore")
        .decode()
    )

    # keep only whitelisted chars
    cleaned_filename = "".join(c for c in cleaned_filename if c in whitelist)
    if len(cleaned_filename) > CHAR_LIMIT:
        print(
            f"Warning, filename truncated because it was over {CHAR_LIMIT}. Filenames may no longer be unique"
        )
    # Truncate filename to avoid possible errors with Windows
    return cleaned_filename[:CHAR_LIMIT]


class ValidateFileUpload:
    def __init__(
        self,
        max_upload_size: Optional[int] = None,
        accepted_content_types: Optional[List[str]] = None,
    ):
        self.max_upload_size = max_upload_size
        self.accepted_content_types = accepted_content_types

    def __call__(self, request: Request):
        if request.method == "POST":
            if self.accepted_content_types is not None:
                if "content-type" not in request.headers:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="content-type not found in header",
                    )
                if (
                    request.headers["content-type"]
                    not in self.accepted_content_types
                ):
                    print(request.headers["content-type"])
                    raise HTTPException(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail=f"We accept only the following file types: {self.accepted_content_types}",
                    )
            if self.max_upload_size is not None:
                if "content-length" not in request.headers:
                    raise HTTPException(
                        status_code=status.HTTP_411_LENGTH_REQUIRED
                    )
                content_length = int(request.headers["content-length"])
                if content_length > self.max_upload_size:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                    )
