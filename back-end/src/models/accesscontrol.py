"""Data models for experiment related endpoints.""" ""
from typing import Dict, List

from pydantic import BaseModel

class AccessControlResponse(BaseModel):
    """Response model for getting an experiment."""

    validUsernames: List[str]
    invalidUsernames: List[str]
    newUsernamesList: List[str]
