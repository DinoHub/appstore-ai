from typing import List
import datetime
from fastapi import APIRouter, Depends, HTTPException, Path, status, Query
from fastapi.responses import JSONResponse, Response
from pymongo import errors as pyerrs
from pymongo import ASCENDING, DESCENDING

from ..internal.auth import check_is_admin, get_password_hash
from ..internal.db import get_db
from ..models.iam import UserInsert, UserPage

# use openssl rand -hex 32 to generate secret key
ACCESS_TOKEN_EXPIRE_MINUTES = 45


router = APIRouter(prefix="/iam", tags=["IAM"])


@router.post("/add", dependencies=[Depends(check_is_admin)])
async def add_user(
    item: UserInsert,
    db=Depends(get_db),
):
    db, mongo_client = db
    try:
        item.password = get_password_hash(item.password)
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                user = await db["users"].insert_one(
                    {
                        "userId": item.user_id,
                        "name": item.name,
                        "password": item.password,
                        "adminPriv": item.admin_priv,
                        "lastModified": str(datetime.datetime.now()),
                        "created": str(datetime.datetime.now()),
                    }
                )
                add_user = await db["users"].find_one(
                    {"_id": user.inserted_id},
                    {"_id": False, "password": False},
                )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=f"User of ID: {add_user['userId']} created",
        )
    except pyerrs.DuplicateKeyError:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=f"User with ID of {item.user_id} already exists",
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content="An error occurred",
        )


@router.delete("/delete", dependencies=[Depends(check_is_admin)])
async def delete_user(
    userid: List[str],
    db=Depends(get_db),
):
    db, mongo_client = db
    try:
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                await db["users"].delete_many({"userId": {"$in": userid}})
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found")


@router.put("/edit", dependencies=[Depends(check_is_admin)])
async def update_user(
    user: UserInsert,
    db=Depends(get_db),
):
    db, mongo_client = db
    try:
        user.password = get_password_hash(user.password)
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                await db["users"].update_one(
                    {"userId": user.user_id},
                    {
                        "$set": {
                            "userId": user.user_id,
                            "name": user.name,
                            "password": user.password,
                            "adminPriv": user.admin_priv,
                            "lastModified": str(datetime.datetime.now()),
                        }
                    },
                )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f""
        )
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# list users with pagination
@router.post("/", dependencies=[Depends(check_is_admin)])
async def get_users(
    pages_user: UserPage,
    descending: bool = Query(default=False, alias="desc"),
    sort_by: str = Query(default="userId", alias="sort"),
    db=Depends(get_db),
):
    db, mongo_client = db
    try:
        # check number of documents to skip past
        skips = pages_user.user_num * (pages_user.page_num - 1)
        # lookups for name and admin priv matching
        lookup = {}
        if pages_user.name != None:
            lookup["name"] = {"$regex": pages_user.name, "$options": "i"}
        if pages_user.admin_priv != None:
            lookup["adminPriv"] = pages_user.admin_priv
        # dont skip if 1st page
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                total_rows = await (db["users"].count_documents(lookup))
                if skips <= 0:
                    # find from users in MongodDB exclude ObjectID and convert to list
                    cursor = await (
                        db["users"]
                        .find(lookup, {"_id": False, "password": False})
                        .sort(sort_by, DESCENDING if descending else ASCENDING)
                        .limit(pages_user.user_num)
                    ).to_list(length=pages_user.user_num)
                # else call cursor with skips
                else:
                    # find from users in MongodDB exclude ObjectID and convert to list
                    cursor = await (
                        db["users"]
                        .find(lookup, {"_id": False, "password": False})
                        .sort(sort_by, DESCENDING if descending else ASCENDING)
                        .skip(skips)
                        .limit(pages_user.user_num)
                    ).to_list(length=pages_user.user_num)
                # return documents

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"results": cursor, "total_rows": total_rows},
        )
    except ValueError:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=f""
        )
    except Exception:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
