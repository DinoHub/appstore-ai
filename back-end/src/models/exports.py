"""Data models for exports"""
from datetime import datetime
from typing import List, Optional, Union, Dict

from bson import ObjectId
from pydantic import BaseModel, Field, validator
from ..internal.utils import to_camel_case


class ExportsPage(BaseModel):
    """Request model for finding logs of the exports"""

    page_num: int = 1
    exports_num: int = 5
    userId: str = ""
    time_initiated_range: Union[str, dict, None] = {"from": "", "to": ""}
    time_completed_range: Union[str, dict, None] = {"from": "", "to": ""}

    @validator("userId")
    def id_is_empty(cls, v: str) -> Optional[str]:
        """Validate user id search field is not empty

        Args:
            v (str): User id

        Returns:
            Optional[str]: user id if not empty, None if empty
        """
        if v.strip() == "":
            return None
        return v

    @validator("time_initiated_range")
    def time_initiated_check(cls, v: Dict) -> Optional[Dict]:
        """Check if time initiated search range is empty

        Args:
            v (Dict): Time initiated search range

        Returns:
            Optional[Dict]: Search range if not empty, None if empty
        """
        if v["from"] == "" or v["to"] == "" or v == "":
            return None
        return v

    @validator("time_completed_range")
    def time_completed_check(cls, v: Dict) -> Optional[Dict]:
        """Check if time completed search range is empty

        Args:
            v (Dict): Time completed search range

        Returns:
            Optional[Dict]: Search range if not empty, None if empty
        """
        if v["from"] == "" or v["to"] == "" or v == "":
            return None
        return v


class ExportLog(BaseModel):

    userId: str = ""
    time_initiated: str = ""
    time_completed: str = ""

    class Config:
        """Pydantic config to allow creation of data model
        from a JSON object with camelCase keys.
        """

        alias_generator = to_camel_case
        arbitrary_types_allowed = True

class ExportLogPackage(BaseModel):

    logs_package: List[ExportLog]
