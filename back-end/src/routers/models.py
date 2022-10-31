import datetime
import json
import re
from typing import List, Optional, Tuple

import httpx
from bson import json_util
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError

from ..config.config import config
from ..internal.auth import get_current_user
from ..internal.db import get_db
from ..internal.file_validator import ValidateFileUpload
from ..internal.utils import uncased_to_snake_case
from ..models.iam import TokenData
from ..models.model import (
    FindModelCardModel,
    ModelCardModelDB,
    ModelCardModelIn,
    UpdateModelCardModel,
)

MAKE_REQUEST_INFERENCE_TIMEOUT = httpx.Timeout(10, read=60 * 5, write=60 * 5)

CHUNK_SIZE = 1024
BytesPerGB = 1024 * 1024 * 1024


ACCEPTED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "video/mp4",
    "video/x-m4v",
    "video/x-matroska",
    "video/webm",
    "video/mpeg" "audio/x-wav",
    "audio/mp4",
    "audio/mpeg",
    "audio/midi",
    "audio/aac",
}

file_validator = ValidateFileUpload(
    max_upload_size=config.MAX_UPLOAD_SIZE_GB * BytesPerGB
)
router = APIRouter(prefix="/models", tags=["Models"])


@router.get("/")
async def search_cards(
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
    page: int = Query(default=1, alias="p", gt=0),
    rows_per_page: int = Query(default=10, alias="n", gt=0),
    descending: bool = Query(default=False, alias="desc"),
    sort_by: str = Query(default="last_modified", alias="sort"),
    title: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None, alias="tag"),
    frameworks: Optional[List[str]] = Query(None, alias="framework"),
    creator_user_id: Optional[str] = Query(None, alias="creator"),
    return_attr: Optional[List[str]] = Query(None, alias="return"),
    all: Optional[bool] = Query(None),
):
    db, client = db
    query = {}
    if title:
        query["title"] = {"$regex": re.escape(title), "$options": "i"}
    if tags:
        query["tags"] = {"$all": tags}
    if frameworks:
        query["frameworks"] = {"$all": frameworks}
    if creator_user_id:
        query["creatorUserId"] = creator_user_id

    # How many documents to skip
    if not all:
        pagination_ptr = (page - 1) * rows_per_page
    else:
        pagination_ptr = 0
        rows_per_page = 0

    # TODO: Refactor pagination method to be more efficient
    async with await client.start_session() as session:
        async with session.start_transaction():
            results = await (
                db["models"]
                .find(query, projection=return_attr)
                .sort(sort_by, DESCENDING if descending else ASCENDING)
                .skip(pagination_ptr)
                .limit(rows_per_page)
            ).to_list(length=rows_per_page if rows_per_page != 0 else None)
    results = json.loads(json_util.dumps(results))
    return results


@router.get("/{creator_user_id}")
async def get_model_cards_by_user(
    creator_user_id: str,
    db=Depends(get_db),
    return_attr: Optional[List[str]] = Query(None, alias="return"),
):
    results = await search_cards(
        db=db,
        all=True,
        return_attr=return_attr,
        creator_user_id=creator_user_id,
    )
    return results


@router.get("/{creator_user_id}/{model_id}")
async def get_model_card_by_id(
    model_id: str, creator_user_id: str, db=Depends(get_db)
):
    db, _ = db
    # Get model card by database id (NOT clearml id)
    model = await db["models"].find_one(
        {"modelId": model_id, "creatorUserId": creator_user_id}
    )
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    model = json.loads(json_util.dumps(model))
    return JSONResponse(status_code=status.HTTP_200_OK, content=model)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_model_card_metadata(
    card: ModelCardModelIn,
    db=Depends(get_db),
    user: TokenData = Depends(get_current_user),
):
    # NOTE: After this, still need to submit inference engine
    db, mongo_client = db
    card.tags = set(card.tags)  # remove duplicates
    card.frameworks = set(card.frameworks)
    card = jsonable_encoder(
        ModelCardModelDB(
            **card.dict(),
            creator_user_id=user["userId"],
            model_id=uncased_to_snake_case(card.title),
            last_modified=datetime.datetime.now(),
            created=datetime.datetime.now(),
        ),
        by_alias=True,  # Convert snake_case to camelCase
    )
    async with await mongo_client.start_session() as session:
        try:
            async with session.start_transaction():
                await db["models"].insert_one(card)
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unable to add model with user and ID {card['creatorUserId']}/{card['modelId']} as the ID already exists.",
            )
    return card


@router.put("/{creator_user_id}/{model_id}", response_model=ModelCardModelDB)
async def update_model_card_metadata_by_id(
    model_id: str,
    creator_user_id: str,
    card: UpdateModelCardModel,
    db=Depends(get_db),
    user: TokenData = Depends(get_current_user),
):
    db, mongo_client = db
    # by alias => convert snake_case to camelCase
    card = {k: v for k, v in card.dict(by_alias=True).items() if v is not None}
    card["lastModified"] = str(datetime.datetime.now())
    if len(card) > 0:
        # perform transaction to ensure we can roll back changes
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                # First, check that user actually has access
                existing_card = await db["models"].find_one(
                    {"modelId": model_id, "creatorUserId": creator_user_id}
                )
                if existing_card is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Model Card with ID: {model_id} not found",
                    )
                elif existing_card["creatorUserId"] != user["userId"]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="User does not have editor access to this model card",
                    )
                else:
                    result = await db["models"].update_one(
                        {
                            "modelId": model_id,
                            "creatorUserId": creator_user_id,
                        },
                        {"$set": card},
                    )
                    if (
                        result.modified_count == 1
                    ):  # NOTE: how pythonic is this? (seems to violate DRY)
                        # TODO: consider just removing the lines below
                        if (
                            updated_card := await db["models"].find_one(
                                {
                                    "modelId": model_id,
                                    "creatorUserId": creator_user_id,
                                }
                            )
                        ) is not None:
                            return updated_card
    # If no changes, try to return existing card
    return existing_card

    # TODO: Might need to update inference engine


@router.delete(
    "/{creator_user_id}/{model_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_model_card_by_id(
    model_id: str,
    creator_user_id: str,
    db=Depends(get_db),
    user: TokenData = Depends(get_current_user),
):
    # TODO: Check that user is the owner of the model card
    db, mongo_client = db
    async with await mongo_client.start_session() as session:
        async with session.start_transaction():
            # First, check that user actually has access
            existing_card = await db["models"].find_one(
                {"modelId": model_id, "creatorUserId": creator_user_id}
            )
            if (
                existing_card is not None
                and existing_card["creatorUserId"] != user["userId"]
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have editor access to this model card",
                )
            await db["models"].delete_one(
                {"modelId": model_id, "creatorUserId": creator_user_id}
            )
    # https://stackoverflow.com/questions/6439416/status-code-when-deleting-a-resource-using-http-delete-for-the-second-time
    # TODO: Should actual model be deleted as well?
