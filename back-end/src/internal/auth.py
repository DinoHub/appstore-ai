from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from ..config.config import config
from ..models.iam import TokenData, User, UserRoles
from .db import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    data: dict, expires_delta: Union[timedelta, None] = None
) -> str:
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db=Depends(get_db)
) -> User:
    db, mongo_client = db
    try:
        payload = jwt.decode(
            token, config.SECRET_KEY, algorithms=[config.ALGORITHM]
        )
        userid: str = payload.get("sub")
        role: UserRoles = payload.get("role")  # Verify that role is correct
        if userid is None or role is None:
            raise CREDENTIALS_EXCEPTION
        token_data = TokenData(userid=userid, role=role)
    except JWTError:
        raise CREDENTIALS_EXCEPTION
    async with await mongo_client.start_session() as session:
        async with session.start_transaction():
            user: Optional[User] = await db["users"].find_one(
                {
                    "userid": token_data.userid,
                    "admin_priv": token_data.role == UserRoles.admin,
                }
            )
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user


async def check_is_admin(token: str = Depends(oauth2_scheme)) -> User:
    user = await get_current_user(token)
    if not user["admin_priv"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have admin access",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        return user
