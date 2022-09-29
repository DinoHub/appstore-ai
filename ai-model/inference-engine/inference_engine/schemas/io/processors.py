import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Union

from fastapi import UploadFile
from pydantic import ValidationError

from ...utils.io import download_file


def check_files_exist(file: str) -> str:
    if not Path(file).exists():
        raise ValidationError(f"Media file not found: {file}")
    return file


def check_single_file(media: List[str]) -> List[str]:
    if len(media) != 1:
        raise ValidationError("Expect only a single file")
    return media


def check_valid_dict(text: Any) -> Dict:
    if isinstance(text, dict):
        return text
    raise ValidationError("Not a valid dictionary!")


def process_input_media_files(media: List[UploadFile]) -> List[str]:
    try:
        media = [download_file(file) for file in media]
    except IOError as e:
        raise ValidationError(f"Failed to download files: {e}")


def process_json(text: str) -> Dict:
    if isinstance(text, dict):
        return text
    try:
        text: Dict = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Failed to process input text as JSON: {e}")


def process_text(text: Union[str, Dict]) -> str:
    if text is None:
        raise ValidationError("No input provided")
    if isinstance(text, Mapping):
        try:
            text = str(text["text"])
        except KeyError:
            raise ValidationError(
                "Text not found in the 'text' field of the JSON"
            )
    if not isinstance(text, str):
        raise ValidationError(f"Invalid input type: {type(text)}")
    return text
