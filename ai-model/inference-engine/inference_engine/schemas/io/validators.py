from pathlib import Path
from typing import List

from pydantic import ValidationError


def check_files_exist(file: str) -> str:
    if not Path(file).exists():
        raise ValidationError(f"Media file not found: {file}")
    return file


def check_single_file(media: List[str]) -> List[str]:
    if len(media) != 1:
        raise ValidationError("Expect only a single file")
    return media
