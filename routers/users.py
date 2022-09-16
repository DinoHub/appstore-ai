import json
from typing import List, Mapping, Optional, Union
from xmlrpc.client import ResponseError

from bson import json_util
from clearml import Model, Task
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse,Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from internal.clearml_client import clearml_client
from internal.db import db, mongo_client
from models.user import UserInsert,UserInsertDB,UserEdit
from pymongo import errors as pyerrs

SECRET_KEY = 'ef3bf6fad7742202730566ed48e140b7fb2b7439169cc6a45f9d8e3230a0a3a5'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


router = APIRouter(prefix="/users",tags=["Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

@router.post('/add')
async def add_user(item: UserInsert):
    try:
        item.password = get_password_hash(item.password)
        item = jsonable_encoder(item)
        user = await db["users"].insert_one(item)
        add_user = await db["users"].find_one({"_id": user.inserted_id})
        add_user = jsonable_encoder(UserInsertDB(**add_user))
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=add_user)
    except pyerrs.DuplicateKeyError:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content=f'Userid of {item.userid} already exists')
    except:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content="An error occurred")

@router.delete('/delete')
async def delete_user(userid: List [str]):
    try:
        delete_result = await db["users"].delete_many({"userid": {"$in": userid}})
        return Response(status_code=204)
    except:
        raise HTTPException(status_code=404, detail=f"Not found")

@router.put("/edit")
async def update_user(user:  List [UserInsert]):
        id_list =[]
        for x in user:
            try:
                x.password = get_password_hash(x.password)
                update_result = await db["users"].update_one({"userid": x.userid}, {"$set": jsonable_encoder(UserEdit(**jsonable_encoder(x)))})
                id_list.append(x.userid)
            except:
                raise HTTPException(status_code=404, detail=f"Not found")
        return Response(status_code=204)
    