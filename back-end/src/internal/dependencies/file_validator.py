"""Module for validating file uploads."""
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
    """Exception raised when file size exceeds upload limit."""

    def __init__(self, fs: int):
        """Initialize a MaxFileSizeException.

        Args:
            fs (int): Total bytes consumed when this exception was raised.
        """
        self.fs = fs


class MaxFileSizeValidator:
    """Validates that file size does not exceed max size."""

    def __init__(self, max_size: int):
        """Initialize a MaxFileSizeValidator.

        Args:
            max_size (int): Max file size in bytes
        """
        self.fs = 0
        self.max_size = max_size

    def __call__(self, chunk: bytes):
        """Consume a chunk of bytes

        Args:
            chunk (bytes): Bytes from file upload

        Raises:
            MaxFileSizeException: If total chunks consumed
                exceeds max size, then file size is too large.
        """
        self.fs += len(chunk)
        if self.fs > self.max_size:
            raise MaxFileSizeException(fs=self.fs)


def determine_safe_file_size(
    path: str = "/", clearance: Union[int, float] = 5
) -> int:
    """Determine the safe file size for a given path.
    This is done to determine if there is enough space
    for decompressing a file.

    Args:
        path (str, optional): Path to check disk usage for. Defaults to "/".
        clearance (Union[int, float], optional): Expected compression ratio. Defaults to 5.

    Returns:
        int: How many bytes can be safely written to disk.
    """
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
    """Validates incoming request to check if file upload is valid."""

    def __init__(
        self,
        max_upload_size: Optional[int] = None,
        accepted_content_types: Optional[List[str]] = None,
    ):
        """Initialize a ValidateFileUpload.

        Args:
            max_upload_size (Optional[int], optional): Maximum upload size in bytes. Defaults to None.
            accepted_content_types (Optional[List[str]], optional): List of accepted MIME types. Defaults to None.
        """
        self.max_upload_size = max_upload_size
        self.accepted_content_types = accepted_content_types

    def __call__(self, request: Request):
        """Intercept incoming request and validate it.

        Args:
            request (Request): Incoming HTTP POST request

        Raises:
            HTTPException: If request does not contain a content-type header.
            HTTPException: If content-type is not in accepted_content_types.
            HTTPException: If request does not contain a content-length header.
            HTTPException: If content-length is greater than max_upload_size.
        """
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
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File is too large. Max size is {self.max_upload_size}, file size is {content_length}",
                    )
