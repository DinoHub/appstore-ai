from pathlib import Path
from typing import Any, Dict, List, Mapping, Union


def check_files_exist(files: List[str]) -> List[str]:
    """Check if file path exists.

    :param files: List of File paths
    :type files: List[str]
    :raises ValidationError: If file path does not exist
    :return: File paths
    :rtype: List[str]
    """
    for file in files:
        if not Path(file).exists():
            raise FileNotFoundError(f"Media file not found: {file}")
    return files


def check_valid_dict(text: Any) -> Dict:
    """Validate that input is valid dictionary.
    This is needed as pydantic will always fail to validate a dictionary.

    :param text: input to validate
    :type text: Any
    :raises ValidationError: If input is not a valid dictionary
    :return: the input
    :rtype: Dict
    """
    if isinstance(text, dict):
        return text
    raise TypeError("Not a valid dictionary!")


def process_text(text: Union[str, Dict]) -> str:
    """Process TextIO to convert it from JSON
    to just extract the single `text` field.

    If already a string, just return it.

    :param text: Dictionary containing `text` key
    :type text: Union[str, Dict]
    :raises ValidationError: If no input is provided
    :raises ValidationError: If input does not have `text` key
    :raises ValidationError: If input is not a dictionary or a string
    :return: text that was in the dictionary
    :rtype: str
    """
    if text is None:
        raise ValueError("No input provided")
    if isinstance(text, Mapping):
        try:
            text = str(text["text"])
        except KeyError:
            raise KeyError("Text not found in the 'text' field of the JSON")
    if not isinstance(text, str):
        raise TypeError(f"Invalid input type: {type(text)}")
    return text
