"""Data models for exports"""
from datetime import datetime
from typing import List, Optional, Union

from bson import ObjectId
from pydantic import BaseModel, Field, validator


class ExportsPage(BaseModel):
    """Request model for finding logs of the exports"""

    page_num: int = 1
    exports_num: int = 5
    userId: str = ""
    time_initiated_range: Union[str, dict, None] = {"from": "", "to": ""}
    time_created_range: Union[str, dict, None] = {"from": "", "to": ""}
