from datetime import datetime
from enum import Enum
from typing import Optional

from bson import ObjectId
from password_strength import PasswordPolicy
from pydantic import BaseModel, Field, validator

from .common import PyObjectId

policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=1,  # need min. 1 uppercase letters
    numbers=1,  # need min. 1 digits
    special=1,  # need min. 1 special characters
)


class UserRoles(str, Enum):
    user = "user"
    admin = "admin"


class UserInsert(BaseModel):
    userid: str
    name: str
    password: str
    password_confirm: str
    admin_priv: bool = False

    @validator("password_confirm")
    def match_passwords(cls, v, values, **kwargs):
        if v != values["password"]:
            raise ValueError("Passwords do not match")
        strength = policy.test(values["password"])
        if not strength:
            return v
        raise ValueError(
            "Password must at least be length of 8, have 1 uppercase letter, 1 number and 1 special character"
        )


class UserInsertDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    userid: str
    name: str
    admin_priv: bool = False

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    userid: Optional[str] = None
    name: Optional[str] = None
    role: Optional[UserRoles] = None
    exp: Optional[datetime] = None


class User(BaseModel):
    userid: str


class UserInDB(User):
    hashed_password: str


class UserPage(BaseModel):
    user_num: int
    name: str = ""
    admin_priv: int = 2

    @validator("user_num")
    def num_of_user_more_than_one(cls, v):
        if v <= 0:
            raise ValueError("Number of users displayed must be more than one")
        return v

    @validator("name")
    def name_is_empty(cls, v):
        if v.strip() == "":
            return None
        return v

    @validator("admin_priv")
    def admin_priv_check(cls, v):
        if v == 0:
            return False
        elif v == 1:
            return True
        else:
            return None
