from datetime import datetime, timedelta
from typing import Union

from fastapi import Depends, HTTPException, Request, status
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext


from ..config.config import config
from ..models.iam import TokenData, UserRoles
from ..models.auth import CsrfSettings, OAuth2PasswordBearerWithCookie
from .db import get_db


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/auth/")


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
    try:
        to_encode = data.copy()
        if expires_delta is not None:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=360)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            config.SECRET_KEY,
            algorithm=config.ALGORITHM,
        )
        return encoded_jwt
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"Token failed to encode",
        )


def decode_jwt(token: str) -> TokenData:
    payload = jwt.decode(
        token,
        config.SECRET_KEY,
        algorithms=[config.ALGORITHM],
    )
    return TokenData(
        user_id=payload.get("sub", None),
        name=payload.get("name", None),
        role=payload.get("role", None),
        exp=payload.get("exp", None),
    )


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_db),
    csrf: CsrfProtect = Depends(),
) -> TokenData:
    db, mongo_client = db
    try:
        csrf.validate_csrf_in_cookies(request)
        token_data = decode_jwt(token)
        if token_data.user_id is None or token_data.role is None:
            raise CREDENTIALS_EXCEPTION
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Token Expired",
        )
    except (JWTError, CsrfProtectError):
        raise CREDENTIALS_EXCEPTION
    async with await mongo_client.start_session() as session:
        async with session.start_transaction():
            user = await db["users"].find_one(
                {
                    "userId": token_data.user_id,
                    "adminPriv": token_data.role == UserRoles.admin,
                }
            )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return token_data


async def check_is_admin(
    request: Request,
    token: str = Depends(oauth2_scheme),
    csrf: CsrfProtect = Depends(),
    db=Depends(get_db),
) -> TokenData:
    user = await get_current_user(request, token, db=db, csrf=csrf)
    if user.role != UserRoles.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have admin access",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        return user
