from aifc import Error
from datetime import datetime, timedelta
from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import JSONResponse, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo import errors as pyerrs

from ..config.config import admin
from ..internal.db import get_db
from ..models.iam import Token, TokenData, User, UserInsert, UserPage

# use openssl rand -hex 32 to generate secret key
ACCESS_TOKEN_EXPIRE_MINUTES = 45


router = APIRouter(prefix="/iam", tags=["IAM"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/iam/auth")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(
    data: dict, expires_delta: Union[timedelta, None] = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, admin.SECRET_KEY, algorithm=admin.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db=Depends(get_db)
):
    db, mongo_client = db
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, admin.SECRET_KEY, algorithms=[admin.ALGORITHM]
        )
        userid: str = payload.get("sub")
        if userid is None:
            raise credentials_exception
        token_data = TokenData(userid=userid)
    except JWTError:
        raise credentials_exception
    async with await mongo_client.start_session() as session:
        async with session.start_transaction():
            user = await db["users"].find_one({"userid": token_data.userid})
    if user is None:
        raise credentials_exception
    return user


@router.post("/add")
async def add_user(
    item: UserInsert,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    db, mongo_client = db
    try:
        item.password = get_password_hash(item.password)
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                user = await db["users"].insert_one(
                    {
                        "userid": item.userid,
                        "name": item.name,
                        "password": item.password,
                        "admin_priv": item.admin_priv,
                    }
                )
                add_user = await db["users"].find_one(
                    {"_id": user.inserted_id},
                    {"_id": False, "password": False},
                )
        print(add_user)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=f"User of ID: {add_user['userid']} created",
        )
    except pyerrs.DuplicateKeyError:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=f"User with ID of {item.userid} already exists",
        )
    except Error as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content="An error occurred",
        )


@router.delete(
    "/delete",
)
async def delete_user(
    userid: List[str],
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    db, mongo_client = db
    try:
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                delete_result = await db["users"].delete_many(
                    {"userid": {"$in": userid}}
                )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found"
        )


@router.put("/edit")
async def update_user(
    user: UserInsert,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    db, mongo_client = db
    try:
        user.password = get_password_hash(user.password)
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                await db["users"].update_one(
                    {"userid": user.userid},
                    {
                        "$set": {
                            "userid": user.userid,
                            "name": user.name,
                            "password": user.password,
                            "admin_priv": user.admin_priv,
                        }
                    },
                )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f""
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/auth", response_model=Token)
async def auth_user_admin(
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
                    if user["admin_priv"] is True:
                        access_token_expires = timedelta(
                            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
                        )
                        access_token = create_access_token(
                            data={"sub": user["userid"]},
                            expires_delta=access_token_expires,
                        )
                        return {
                            "access_token": access_token,
                            "token_type": "bearer",
                        }
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User is not admin",
                            headers={"WWW-Authenticate": "Bearer"},
                        )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Password is wrong",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User ID does not exist",
                    headers={"WWW-Authenticate": "Bearer"},
                )


# check whether user is authenticated and has admin priv
@router.get("/check", response_model=User)
async def check_user_admin(current_user: User = Depends(get_current_user)):
    if current_user["admin_priv"] is True:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"User is not admin",
        headers={"WWW-Authenticate": "Bearer"},
    )


# list users with pagination
@router.post("/{page_num}")
async def get_users(
    pages_user: UserPage,
    page_num: int = Path(ge=1),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    db, mongo_client = db
    if current_user["admin_priv"] is True:
        try:
            # check number of documents to skip past
            skips = pages_user.user_num * (page_num - 1)
            # lookups for name and admin priv matching
            lookup = {}
            if pages_user.name != None:
                lookup["name"] = {"$regex": pages_user.name, "$options": "i"}
            if pages_user.admin_priv != None:
                lookup["admin_priv"] = pages_user.admin_priv
            # dont skip if 1st page
            async with await mongo_client.start_session() as session:
                async with session.start_transaction():
                    if skips <= 0:
                        # find from users in MongodDB exclude ObjectID and convert to list
                        cursor = await (
                            db["users"]
                            .find(lookup, {"_id": False, "password": False})
                            .limit(pages_user.user_num)
                        ).to_list(length=pages_user.user_num)
                    # else call cursor with skips
                    else:
                        # find from users in MongodDB exclude ObjectID and convert to list
                        cursor = await (
                            db["users"]
                            .find(lookup, {"_id": False, "password": False})
                            .skip(skips)
                            .limit(pages_user.user_num)
                        ).to_list(length=pages_user.user_num)
                    # return documents
            return JSONResponse(status_code=status.HTTP_200_OK, content=cursor)
        except ValueError as e:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=f""
            )
        except:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # ensure when loading this endpoint that user is authenticateds not admin",headers={"WWW-Authenticate": "Bearer"})
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"User is not admin",
        headers={"WWW-Authenticate": "Bearer"},
    )
