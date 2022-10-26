from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_csrf_protect import CsrfProtect
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from ..config.config import config
from ..models.iam import CsrfSettings, TokenData, User, UserRoles
from .db import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()


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
        expire = datetime.utcnow() + timedelta(minutes=360)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        config.SECRET_KEY
        if to_encode["role"] == UserRoles.user
        else config.ADMIN_SECRET_KEY,
        algorithm=config.ALGORITHM,
    )
    return encoded_jwt


def decode_jwt(token: str, is_admin: bool = False) -> TokenData:
    payload = jwt.decode(
        token,
        config.ADMIN_SECRET_KEY if is_admin else config.SECRET_KEY,
        algorithms=[config.ALGORITHM],
    )
    return TokenData(
        userid=payload.get("sub", None),
        name=payload.get("name", None),
        role=payload.get("role", None),
        exp=payload.get("exp", None),
    )


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_db),
    csrf: CsrfProtect = Depends(),
    is_admin: bool = False,
) -> User:
    csrf.validate_csrf_in_cookies(request)
    db, mongo_client = db
    try:
        token_data = decode_jwt(token, is_admin)
        if token_data.userid is None or token_data.role is None:
            raise CREDENTIALS_EXCEPTION
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Token Expired",
        )
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


async def check_is_admin(
    request: Request, token: str = Depends(oauth2_scheme), db=Depends(get_db)
) -> User:
    user = await get_current_user(request, token, db=db, is_admin=True)
    if not user["admin_priv"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have admin access",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        return user
