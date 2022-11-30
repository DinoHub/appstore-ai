from datetime import datetime
from enum import Enum
from typing import Optional, List
import secrets

from bson import ObjectId
from password_strength import PasswordPolicy
from pydantic import BaseModel, Field, validator
from typing import Union

from ..internal.utils import to_camel_case
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


class UsersEdit(BaseModel):
    users: List[str] = []
    priv: bool = False


class UserInsert(BaseModel):
    name: str
    user_id: str
    password: str
    password_confirm: str
    admin_priv: bool = False

    @validator("user_id")
    def generate_if_empty(cls, v, values, **kwargs):
        name_string = "".join(values["name"].lower().split())
        if v == None or v == "":
            new_id = f"{name_string[0:7]}-{secrets.token_hex(8)}"
            return new_id
        return v

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
    user_id: str
    name: str
    admin_priv: bool = False

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None
    name: Optional[str] = None
    role: Optional[UserRoles] = None
    exp: Optional[datetime] = None


class User(BaseModel):
    userId: str
    adminPriv: bool


class UserInDB(User):
    hashed_password: str


class UserRemoval(BaseModel):
    users: List[str]


class UserPage(BaseModel):
    page_num: int = 1
    user_num: int = 5
    name: str = ""
    userId: str = ""
    admin_priv: int = 2
    last_modified_range: Union[str, dict, None] = {"from": "", "to": ""}
    date_created_range: Union[str, dict, None] = {"from": "", "to": ""}

    @validator("page_num")
    def page_number_check(cls, v):
        if v <= 0:
            raise ValueError("Page number should be above one")
        return v

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

    @validator("userId")
    def id_is_empty(cls, v):
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

    @validator("last_modified_range")
    def last_modified_check(cls, v):
        if v["from"] == "" or v["to"] == "" or v == "":
            return None
        return v

    @validator("date_created_range")
    def date_created_check(cls, v):
        if v["from"] == "" or v["to"] == "" or v == "":
            return None
        return v
