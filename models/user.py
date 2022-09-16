from typing import Dict, List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from .common import PyObjectId

class UserEdit(BaseModel):
    name: str
    password: str
    admin_priv: bool = False

class UserInsert(BaseModel):
    userid : str
    name: str
    password: str
    admin_priv: bool = False

class UserInsertDB(UserInsert):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}