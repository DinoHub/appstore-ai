"""Data models for experiment related endpoints.""" ""
from typing import Dict, List
from ..internal.utils import to_camel_case

from pydantic import BaseModel

class AccessControlResponse(BaseModel):
    """Response model for getting an experiment."""

    valid_usernames: List[str]
    invalid_usernames: List[str]
    new_usernames_list: List[str]

    class Config:
        """Pydantic config to allow creation of data model
        from a JSON object with camelCase keys.
        """
        alias_generator = to_camel_case
