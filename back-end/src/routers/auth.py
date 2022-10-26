from datetime import timedelta

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_csrf_protect import CsrfProtect
from jose import ExpiredSignatureError, JWTError

from ..internal.auth import (
    CREDENTIALS_EXCEPTION,
    check_is_admin,
    create_access_token,
    decode_jwt,
    verify_password,
)
from ..internal.db import get_db
from ..models.iam import Token, UserRoles

# use openssl rand -hex 32 to generate secret key
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 43200  # 30 Days

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/", response_model=Token)
async def auth_user(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_db),
):
    db, mongo_client = db
    csrf = CsrfProtect()
    async with await mongo_client.start_session() as session:
        async with session.start_transaction():
            if (
                user := await db["users"].find_one(
                    {"userid": form_data.username}
                )
            ) is not None:
                if (
                    verify_password(form_data.password, user["password"])
                    is True
                ):
                    data = {
                        "sub": user["userid"],
                        "role": UserRoles.admin
                        if user["admin_priv"]
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
                        detail=f"Invalid password",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User ID does not exist",
                    headers={"WWW-Authenticate": "Bearer"},
                )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
    db=Depends(get_db),
):
    try:
        form = await request.json()
        if form.get("grant_type") == "refresh_token":
            rs = form.get("refresh_token")
            token_data = decode_jwt(
                rs,
                is_admin=form.get("role") == UserRoles.admin,
            )
            db, mongo_client = db
            async with await mongo_client.start_session() as session:
                async with session.start_transaction():
                    if (
                        user := await db["users"].find_one(
                            {"userid": token_data.userid}
                        )
                    ) is not None:
                        data = {
                            "sub": user["userid"],
                            "role": UserRoles.admin
                            if user["admin_priv"]
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
                            detail=f"User ID does not exist",
                            headers={"WWW-Authenticate": "Bearer"},
                        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Refresh Token Expired, you will need to logout and log back in to create a new refresh token.",
        )
    except JWTError:
        raise CREDENTIALS_EXCEPTION
    raise CREDENTIALS_EXCEPTION


@router.get(
    "/is_admin",
    dependencies=[Depends(check_is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
def verify_admin():
    """This endpoint mostly exists just to test that auth code is working"""
    return
