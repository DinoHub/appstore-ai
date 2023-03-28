import datetime
from typing import Dict, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from pymongo import errors as pyerrs

from ..internal.auth import check_is_admin, get_password_hash
from ..internal.dependencies.mongo_client import get_db
from ..internal.utils import sanitize_for_url, uncased_to_snake_case
from ..models.iam import UserInsert, UserPage, UserRemoval, UsersEdit

# use openssl rand -hex 32 to generate secret key
ACCESS_TOKEN_EXPIRE_MINUTES = 45


router = APIRouter(prefix="/iam", tags=["IAM"])


@router.post("/add", dependencies=[Depends(check_is_admin)])
async def add_user(
    item: UserInsert,
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
):
    """
    Function to add a user to the MongoDB after reciveing a POST call to the endpoint

    Args:
        item (UserInsert): The item that contains the user information to be sent to the database for storage
        db (Any = Depends(get_db)): This retieves the client that is connected to the database.

    Returns:
        JSONResponse: A Response object with a corresponding code depending on the success of the call or a failure for whatever reason.
    """
    db, mongo_client = db
    try:
        item.password = get_password_hash(item.password.get_secret_value())
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                user = await db["users"].insert_one(
                    {
                        "userId": uncased_to_snake_case(item.user_id),
                        "name": item.name,
                        "password": item.password,
                        "adminPriv": item.admin_priv,
                        "lastModified": str(datetime.datetime.now()),
                        "created": str(datetime.datetime.now()),
                    }
                )
                added_user = await db["users"].find_one(
                    {"_id": user.inserted_id},
                    {"_id": False, "password": False},
                )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=f"User of ID: {added_user['userId']} created",
        )
    except pyerrs.DuplicateKeyError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with ID of {item.user_id} already exists",
        ) from err
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred",
        ) from err


@router.delete(
    "/delete",
    dependencies=[Depends(check_is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    userid: UserRemoval,
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
) -> None:
    """Delete a user from the database

    Args:
        userid (UserRemoval): User ID to delete
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB connection.
            Defaults to Depends(get_db).

    Raises:
        HTTPException: 404 if user not found
    """
    db, mongo_client = db
    try:
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                await db["users"].delete_many({"userId": {"$in": userid.users}})
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        ) from err


@router.put(
    "/edit",
    dependencies=[Depends(check_is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_user(
    user: UserInsert,
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
):
    """Edit a single user from the database

    Args:
        user (UserInsert): User to edit
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB connection.
            Defaults to Depends(get_db).

    Raises:
        HTTPException: 404 if user not found
        HTTPException: 422 if value error occurs
    """
    db, mongo_client = db
    try:
        user.password = get_password_hash(user.password.get_secret_value())
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
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to update user",
        ) from err
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        ) from err


@router.put(
    "/edit/multi",
    dependencies=[Depends(check_is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_many_user(
    user: UsersEdit,
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
):
    """Bulk edit many users' privileges in the database

    Args:
        user (UsersEdit): Users to edit
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB connection.
            Defaults to Depends(get_db).

    Raises:
        HTTPException: 400 if privilege to change to was not defined
        HTTPException: 404 if users not found
        HTTPException: 422 if value error occurs
    """
    db, mongo_client = db
    try:
        if user.priv is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Privilege must be set properly",
            )
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                await db["users"].update_many(
                    {"userId": {"$in": user.users}},
                    {
                        "$set": {
                            "adminPriv": user.priv,
                            "lastModified": str(datetime.datetime.now()),
                        }
                    },
                )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to update users",
        ) from err
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
        ) from err


# list users with pagination
@router.post("/", dependencies=[Depends(check_is_admin)])
async def get_users(
    pages_user: UserPage,
    descending: bool = Query(default=True, alias="desc"),
    sort_by: str = Query(default="lastModified", alias="sort"),
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
) -> Dict:
    """Get a list of users from the database

    Args:
        pages_user (UserPage): Pagination input
        descending (bool, optional): Order of results. Defaults to Query(default=True, alias="desc").
        sort_by (str, optional): Sort field. Defaults to Query(default="lastModified", alias="sort").
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB connection.
            Defaults to Depends(get_db).

    Raises:
        HTTPException: 422 if unable to get users
        HTTPException: 404 if user not found

    Returns:
        Dict: _description_
    """
    db, mongo_client = db
    try:
        # check number of documents to skip past
        skips = pages_user.user_num * (pages_user.page_num - 1)
        # dictionary for lookups
        lookup = {}
        # narrow search by users that include given name from request if not none
        if pages_user.name is not None:
            lookup["name"] = {"$regex": pages_user.name, "$options": "i"}
        # narrow search by users that include given userId from request if not none
        if pages_user.userId is not None:
            lookup["userId"] = {"$regex": pages_user.userId, "$options": "i"}
        # narrow search by looking for users with/without admin priv only based on req
        if pages_user.admin_priv is not None:
            lookup["adminPriv"] = pages_user.admin_priv
        # narrow search by looking for users last modified within a date range given by req
        if pages_user.last_modified_range is not None:
            if isinstance(pages_user.last_modified_range, dict):
                lookup["lastModified"] = {
                    "$gte": pages_user.last_modified_range["from"],
                    "$lte": pages_user.last_modified_range["to"],
                }
        # narrow search by looking for users created within a date range given by req
        if pages_user.date_created_range is not None:
            if isinstance(pages_user.date_created_range, dict):
                lookup["created"] = {
                    "$gte": pages_user.date_created_range["from"],
                    "$lte": pages_user.date_created_range["to"],
                }
        # start session + transaction to get data from MongoDB
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                # check for the total number of rows in 'users' collection
                total_rows = await (db["users"].count_documents(lookup))
                # dont skip if 1st page
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
        # return documents if all ok
        return {"results": cursor, "total_rows": total_rows}
    # triggered if req sent to this endpoint has missing headers or invalid data
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to get users",
        ) from err
    # triggered if all else fails
    except Exception as err:
        # TODO: should the status code be 404?
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cannot find users"
        ) from err
