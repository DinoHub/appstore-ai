"""Authentication Endpoints"""
from datetime import timedelta
from typing import Dict, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from jose import ExpiredSignatureError, JWTError
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ..internal.auth import (
    CREDENTIALS_EXCEPTION,
    check_is_admin,
    create_access_token,
    decode_jwt,
    verify_password,
)
from ..internal.dependencies.mongo_client import get_db
from ..models.iam import Token, UserRoles
from ..config.config import config

# use openssl rand -hex 32 to generate secret key
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 43200  # 30 Days

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/", response_model=Token)
async def auth_user(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
) -> Dict[str, str]:
    """Authenticate user and return access and refresh tokens

    Args:
        response (Response): Response that will be returned to the client
        form_data (OAuth2PasswordRequestForm, optional): Username and Password.
            Defaults to Depends().
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB Connection.
            Defaults to Depends(get_db).

    Raises:
        HTTPException: 401 Unauthorized if credentials are invalid
        HTTPException: 404 Not Found if user does not exist

    Returns:
        Dict[str, str]: Response containing access and refresh tokens. Credentials are saved as cookies.
    """
    db, mongo_client = db
    csrf = CsrfProtect()
    async with await mongo_client.start_session() as session:
        async with session.start_transaction():
            if (
                user := await db["users"].find_one({"userId": form_data.username})
            ) is not None:
                if verify_password(form_data.password, user["password"]) is True:
                    data = {
                        "sub": user["userId"],
                        "role": UserRoles.admin
                        if user["adminPriv"]
                        else UserRoles.user,
                        "name": user["name"],
                    }
                    access_token_expires = timedelta(
                        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
                    )
                    refresh_token_expires = timedelta(
                        minutes=REFRESH_TOKEN_EXPIRE_MINUTES
                    )
                    access_token = create_access_token(
                        data=data,
                        expires_delta=access_token_expires,
                    )
                    refresh_token = create_access_token(
                        data=data, expires_delta=refresh_token_expires
                    )
                    response.set_cookie(
                        "access_token",
                        value=f"Bearer {access_token}",
                        httponly=True,
                        secure=config.SECURE_COOKIES,
                        expires=60 * ACCESS_TOKEN_EXPIRE_MINUTES,
                        max_age=60 * ACCESS_TOKEN_EXPIRE_MINUTES,
                    )
                    response.set_cookie(
                        "refresh_token",
                        value=f"Bearer {refresh_token}",
                        httponly=True,
                        secure=config.SECURE_COOKIES,
                        expires=60 * REFRESH_TOKEN_EXPIRE_MINUTES,
                        max_age=60 * REFRESH_TOKEN_EXPIRE_MINUTES,
                    )
                    # Protect Cookies with CSRF
                    csrf.set_csrf_cookie(response)

                    return {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": "bearer",
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid password",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User ID does not exist",
                    headers={"WWW-Authenticate": "Bearer"},
                )


@router.post("/refresh", response_model=Token)
async def get_refresh_token(
    request: Request,
    response: Response,
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
    csrf: CsrfProtect = Depends(),
) -> Optional[Dict[str, str]]:
    """Use refresh token to get new access token
    when access token expires.

    Args:
        request (Request): Incoming request
        response (Response): Response that will be returned to the client
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB Connection.
            Defaults to Depends(get_db).
        csrf (CsrfProtect, optional): Perform CSRF protection. Defaults to Depends().

    Raises:
        HTTPException: 404 if user does not exist
        HTTPException: 403 if refresh token expired
        CREDENTIALS_EXCEPTION: 401 if credentials are invalid
        HTTPException: 409 if CSRF token is invalid
        HTTPException: 400 otherwise

    Returns:
        Optional[Dict[str, str]]: Access token if refresh token is valid
    """
    try:
        form = await request.json()
        if form.get("grant_type") == "refresh_token":
            rs = request.cookies["refresh_token"]
            _, param = get_authorization_scheme_param(rs)
            if param:
                token_data = decode_jwt(param)
            else:
                token_data = decode_jwt(rs)
            db, mongo_client = db
            async with await mongo_client.start_session() as session:
                async with session.start_transaction():
                    if (
                        user := await db["users"].find_one(
                            {
                                "userId": token_data.user_id,
                                "adminPriv": token_data.role == UserRoles.admin,
                            }
                        )
                    ) is not None:
                        data = {
                            "sub": user["userId"],
                            "role": UserRoles.admin
                            if user["adminPriv"]
                            else UserRoles.user,
                            "name": user["name"],
                        }
                        access_token_expires = timedelta(
                            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
                        )
                        access_token = create_access_token(
                            data=data,
                            expires_delta=access_token_expires,
                        )
                        response.set_cookie(
                            "access_token",
                            value=f"Bearer {access_token}",
                            httponly=True,
                            secure=config.SECURE_COOKIES,
                            expires=60 * ACCESS_TOKEN_EXPIRE_MINUTES,
                        )
                        csrf = CsrfProtect()
                        csrf.set_csrf_cookie(response)
                        return {
                            "access_token": access_token,
                            "refresh_token": rs,
                            "token_type": "bearer",
                        }
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="User ID does not exist",
                            headers={"WWW-Authenticate": "Bearer"},
                        )
    except ExpiredSignatureError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Refresh Token Expired, you will need to logout and log back in to create a new refresh token.",
        ) from err
    except JWTError as err:
        raise CREDENTIALS_EXCEPTION from err
    except CsrfProtectError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CSRF token was removed or tampered with",
        ) from err
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong access method",
        ) from err


@router.delete("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user(response: Response) -> None:
    """Logout user by deleting cookies

    Args:
        response (Response): Response that will be returned to the client

    Raises:
        HTTPException: 500 if an error occurs
    """
    try:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        response.delete_cookie("fastapi-csrf-token")
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred",
        ) from err


@router.get(
    "/is_admin",
    dependencies=[Depends(check_is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
def verify_admin():
    """This endpoint mostly exists just to test that auth code is working"""
    return
