"""Data models for user management"""
import secrets
from datetime import datetime
from enum import Enum
from typing import Dict, List, Literal, Optional, Union

from password_strength import PasswordPolicy
from pydantic import BaseModel, SecretStr, validator

from ..internal.utils import sanitize_for_url

policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=1,  # need min. 1 uppercase letters
    numbers=1,  # need min. 1 digits
    special=1,  # need min. 1 special characters
)


class UserRoles(str, Enum):
    """Possible user roles."""

    user = "user"
    admin = "admin"


class UsersEdit(BaseModel):
    """Request model for editing many users."""

    users: List[str] = []
    priv: bool = False


class UserInsert(BaseModel):
    """Request model for creating a user."""

    name: str
    user_id: str
    password: SecretStr
    password_confirm: SecretStr
    admin_priv: bool = False

    @validator("user_id")
    def generate_if_empty(
        cls, v: Optional[str], values: Dict, **kwargs
    ) -> str:
        """Generates a user id if one is not provided and sanitize the id for URL safe usage.

        Args:
            v (Optional[str]): The user id.
            values (Dict): User data.

        Returns:
            str: Generated user id.
        """
        # Get name from user data and strip whitespace
        name_string = "".join(values["name"].lower().split())
        # if user id is empty, generate a new one
        if v is None or v == "":
            new_id = (
                f"{sanitize_for_url(name_string[0:7])}_{secrets.token_hex(8)}"
            )
            return new_id
        return sanitize_for_url(v)

    @validator("password_confirm")
    def match_passwords(
        cls, v: SecretStr, values: Dict, **kwargs
    ) -> SecretStr:
        """Checks that password is strong and check confirm password matches.

        Args:
            v (SecretStr): Password
            values (Dict): User data.

        Raises:
            ValueError: If confirmation password does not match password.
            ValueError: If password is not strong.

        Returns:
            str: _description_
        """
        if v != values["password"]:
            raise ValueError("Passwords do not match")
        strength = policy.test(values["password"].get_secret_value())
        if not strength:
            return v
        raise ValueError(
            "Password must at least be length of 8, have 1 uppercase letter, 1 number and 1 special character"
        )


class Token(BaseModel):
    """Data model for user tokens"""

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"]


class TokenData(BaseModel):
    """Decoded JWT token data."""

    user_id: Optional[str] = None
    name: Optional[str] = None
    role: Optional[UserRoles] = None
    exp: Optional[datetime] = None


class User(BaseModel):
    """Data model for user."""

    userId: str
    adminPriv: bool


class UserInDB(User):
    """Data model for user in database."""

    hashed_password: SecretStr


class UserRemoval(BaseModel):
    """Request model for removing many users."""

    users: List[str]


class UserPage(BaseModel):
    """Request model for finding users"""

    page_num: int = 1
    user_num: int = 5
    name: str = ""
    userId: str = ""
    admin_priv: int = 2
    last_modified_range: Union[str, dict, None] = {"from": "", "to": ""}
    date_created_range: Union[str, dict, None] = {"from": "", "to": ""}

    @validator("page_num")
    def page_number_check(cls, v: int) -> int:
        """Validate pagination page number is valid

        Args:
            v (int): Page number

        Raises:
            ValueError: If page number is less than 1

        Returns:
            int: Page number
        """
        if v <= 0:
            raise ValueError("Page number should be above one")
        return v

    @validator("user_num")
    def num_of_user_more_than_one(cls, v: int) -> int:
        """Validate number of users displayed is one or more

        Args:
            v (int): Number of users displayed

        Raises:
            ValueError: If number of users displayed is less than 1

        Returns:
            int: Number of users displayed
        """
        if v <= 0:
            raise ValueError("Number of users displayed must be more than one")
        return v

    @validator("name")
    def name_is_empty(cls, v: str) -> Optional[str]:
        """Check if search name field is empty

        Args:
            v (str): Search name field

        Returns:
            Optional[str]: name if not empty, None if empty
        """
        if v.strip() == "":
            return None
        return v

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

    @validator("admin_priv")
    def admin_priv_check(cls, v: int) -> Optional[bool]:
        """Validate if user is admin

        Args:
            v (int): Admin priv level

        Returns:
            Optional[bool]: True if admin, False if not admin, None if not set
        """
        if v == 0:
            return False
        elif v == 1:
            return True
        else:
            return None

    @validator("last_modified_range")
    def last_modified_check(cls, v: Dict) -> Optional[Dict]:
        """Check if last modified search range is empty

        Args:
            v (Dict): Last modified search range

        Returns:
            Optional[Dict]: Search range if not empty, None if empty
        """
        if v["from"] == "" or v["to"] == "" or v == "":
            return None
        return v

    @validator("date_created_range")
    def date_created_check(cls, v: Dict) -> Optional[Dict]:
        """Check if date created search range is empty

        Args:
            v (Dict): Search range

        Returns:
            Optional[Dict]: Search range if not empty, None if empty
        """
        if v["from"] == "" or v["to"] == "" or v == "":
            return None
        return v
