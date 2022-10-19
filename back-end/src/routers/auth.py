from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..internal.auth import create_access_token, verify_password
from ..internal.db import get_db
from ..models.iam import Token, UserRoles

# use openssl rand -hex 32 to generate secret key
ACCESS_TOKEN_EXPIRE_MINUTES = 45

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/", response_model=Token)
async def auth_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)
):
    db, mongo_client = db
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
                    access_token_expires = timedelta(
                        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
                    )
                    access_token = create_access_token(
                        data={
                            "sub": user["userid"],
                            "role": UserRoles.admin
                            if user["admin_priv"]
                            else UserRoles.user,
                        },
                        expires_delta=access_token_expires,
                    )
                    return {
                        "access_token": access_token,
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
