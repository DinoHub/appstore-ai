"""Authentication internal logic"""
from datetime import datetime, timedelta
from typing import Union

from fastapi import Depends, HTTPException, Request, status
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from ..config.config import config
from ..models.auth import CsrfSettings, OAuth2PasswordBearerWithCookie
from ..models.iam import TokenData, UserRoles
from .dependencies.mongo_client import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/auth/")

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


@CsrfProtect.load_config
def get_csrf_config() -> CsrfSettings:
    """Get CSRF config

    Returns:
        CsrfSettings: Cross-site request forgery protection config
    """
    return CsrfSettings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that password is correct

    Args:
        plain_password (str): Password in plain text
        hashed_password (str): Hashed password

    Returns:
        bool: _description_
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Convert plain text password to hashed password

    Args:
        password (str): Password in plain text

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(
    data: dict, expires_delta: Union[timedelta, None] = None
) -> str:
    """Create access token as JWT for API authentication

    Args:
        data (dict): A claim to be encoded in the JWT.
        expires_delta (Union[timedelta, None], optional): Time taken for token to expire. Defaults to None.

    Raises:
        HTTPException: If no secret key is set in app config
        HTTPException: If unable to encode token

    Returns:
        str: Encoded JWT
    """
    if config.SECRET_KEY is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No secret key set",
        )
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
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Token failed to encode",
        ) from err


def decode_jwt(token: str) -> TokenData:
    """Decode JWT token

    Args:
        token (str): Encoded JWT

    Raises:
        HTTPException: If no secret key is set in app config

    Returns:
        TokenData: Decoded JWT as Pydantic data model
    """
    if config.SECRET_KEY is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No secret key set",
        )
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
    """Get current user from JWT token

    Args:
        request (Request): Incoming HTTP request
        token (str, optional): Encoded JWT. Defaults to Depends(oauth2_scheme).
        db (_type_, optional): MongoDB connection. Defaults to Depends(get_db).
        csrf (CsrfProtect, optional): CSRF Protection. Defaults to Depends().

    Raises:
        CREDENTIALS_EXCEPTION: If token does not provide a user or role
        HTTPException: If token is expired
        CREDENTIALS_EXCEPTION: If token is invalid or CSRF token is invalid
        HTTPException: If token does not reference a valid user

    Returns:
        TokenData: _description_
    """
    db, mongo_client = db
    try:
        csrf.validate_csrf_in_cookies(request)
        token_data = decode_jwt(token)
        if token_data.user_id is None or token_data.role is None:
            raise CREDENTIALS_EXCEPTION
    except ExpiredSignatureError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access Token Expired",
        ) from err
    except (JWTError, CsrfProtectError) as err:
        raise CREDENTIALS_EXCEPTION from err
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
    """Validate that user is an admin

    Args:
        request (Request): Incoming HTTP request
        token (str, optional): Encoded JWT. Defaults to Depends(oauth2_scheme).
        csrf (CsrfProtect, optional): CSRF Protection. Defaults to Depends().
        db (_type_, optional): MongoDB Connection. Defaults to Depends(get_db).

    Raises:
        HTTPException: If user is not an admin

    Returns:
        TokenData: Pydantic data model of user
    """
    user = await get_current_user(request, token, db=db, csrf=csrf)
    if user.role != UserRoles.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have admin access",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        return user
