import datetime
import json
import re
from typing import Dict, List, Optional, Tuple

from bson import json_util
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError

from ..config.config import config
from ..internal.auth import get_current_user
from ..internal.dependencies.mongo_client import get_db
from ..internal.dependencies.file_validator import ValidateFileUpload
from ..internal.preprocess_html import preprocess_html
from ..internal.tasks import delete_orphan_images, delete_orphan_services
from ..internal.utils import uncased_to_snake_case
from ..models.iam import TokenData
from ..models.model import (
    GetFilterResponseModel,
    ModelCardModelDB,
    ModelCardModelIn,
    SearchModelResponse,
    UpdateModelCardModel,
)

CHUNK_SIZE = 1024
BYTES_PER_GB = 1024 * 1024 * 1024


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
    max_upload_size=int(config.MAX_UPLOAD_SIZE_GB * BYTES_PER_GB)
)
router = APIRouter(prefix="/models", tags=["Models"])


@router.get(
    "/_db/options/filters/", response_model=GetFilterResponseModel
)  # prevent accidently matching with user/model id
async def get_available_filters(
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db)
) -> Dict[str, List[str]]:
    """Get available filters for model zoo search page

    Args:
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB connection.
            Defaults to Depends(get_db).

    Returns:
        Dict[str, List[str]]: All available tags, frameworks, and tasks
    """
    # TODO: Optimize retrieval through Redis cache
    db, _ = db
    models = db["models"]
    tags = await models.distinct("tags")
    frameworks = await models.distinct("frameworks")
    tasks = await models.distinct("task")
    return {"tags": tags, "frameworks": frameworks, "tasks": tasks}


@router.get("/{creator_user_id}/{model_id}", response_model=ModelCardModelDB)
async def get_model_card_by_id(
    model_id: str,
    creator_user_id: str,
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
) -> Dict:
    """Get model card by composite ID: creator_user_id/model_id

    Args:
        model_id (str): Model ID to search for
        creator_user_id (str): Creator user ID to search for
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB connection.
            Defaults to Depends(get_db).

    Raises:
        HTTPException: 404 if model card not found

    Returns:
        Dict: Model card
    """
    db, _ = db
    # Get model card by database id (NOT clearml id)
    model = await db["models"].find_one(
        {"modelId": model_id, "creatorUserId": creator_user_id}
    )
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unable to find: {creator_user_id}/{model_id}",
        )
    model = json.loads(json_util.dumps(model))
    return model


@router.get(
    "/", response_model=SearchModelResponse, response_model_exclude_unset=True
)
async def search_cards(
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
    page: int = Query(default=1, alias="p", gt=0),
    rows_per_page: int = Query(default=10, alias="n", ge=0),
    descending: bool = Query(default=False, alias="desc"),
    sort_by: str = Query(default="_id", alias="sort"),
    title: Optional[str] = Query(default=None),
    tasks: Optional[List[str]] = Query(default=None, alias="tasks[]"),
    tags: Optional[List[str]] = Query(default=None, alias="tags[]"),
    frameworks: Optional[List[str]] = Query(
        default=None, alias="frameworks[]"
    ),
    creator_user_id: Optional[str] = Query(default=None, alias="creator"),
    return_attr: Optional[List[str]] = Query(default=None, alias="return[]"),
    all: Optional[bool] = Query(default=None),
) -> Dict:
    """Search model cards

    Args:
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB connection. Defaults to Depends(get_db).
        page (int, optional): Page number. Defaults to Query(default=1, alias="p", gt=0).
        rows_per_page (int, optional): Rows per page. Defaults to Query(default=10, alias="n", ge=0).
        descending (bool, optional): Order to return results in. Defaults to Query(default=False, alias="desc").
        sort_by (str, optional): Sort by field. Defaults to Query(default="_id", alias="sort").
        title (Optional[str], optional): Search by model title. Defaults to Query(default=None).
        tasks (Optional[List[str]], optional): Search by task. Defaults to Query(default=None, alias="tasks[]").
        tags (Optional[List[str]], optional): Search by task. Defaults to Query(default=None, alias="tags[]").
        frameworks (Optional[List[str]], optional): Search by framework. Defaults to Query( default=None, alias="frameworks[]" ).
        creator_user_id (Optional[str], optional): Search by creator. Defaults to Query(default=None, alias="creator").
        return_attr (Optional[List[str]], optional): Which fields to return. Defaults to Query(default=None, alias="return[]").
        all (Optional[bool], optional): Whether to return all results. Defaults to Query(default=None).

    Returns:
        Dict: A dictionary containing the results and pagination information
    """
    db, client = db
    query = {}
    if title:
        query["title"] = {"$regex": re.escape(title), "$options": "i"}
    if tasks:
        query["task"] = {"$in": tasks}
    if tags:
        query["tags"] = {"$all": tags}
    if frameworks:
        query["frameworks"] = {"$in": frameworks}
    if creator_user_id:
        query["creatorUserId"] = creator_user_id

    # How many documents to skip
    if not all or rows_per_page == 0:
        pagination_ptr = (page - 1) * rows_per_page
    else:
        pagination_ptr = 0
        rows_per_page = 0

    # TODO: Refactor pagination method to be more efficient
    async with await client.start_session() as session:
        async with session.start_transaction():
            total_rows = await (db["models"].count_documents(query))
            results = await (
                db["models"]
                .find(query, projection=return_attr)
                .sort(sort_by, DESCENDING if descending else ASCENDING)
                .skip(pagination_ptr)
                .limit(rows_per_page)
            ).to_list(length=rows_per_page if rows_per_page != 0 else None)
    results = json.loads(json_util.dumps(results))
    return {"results": results, "total": total_rows}


@router.get(
    "/{creator_user_id}",
    response_model=SearchModelResponse,
    response_model_exclude_unset=True,
)
async def get_model_cards_by_user(
    creator_user_id: str,
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
    return_attr: Optional[List[str]] = Query(None, alias="return"),
) -> Dict:
    """Get all model cards by a user

    Args:
        creator_user_id (str): Creator user id
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB connection.
            Defaults to Depends(get_db).
        return_attr (Optional[List[str]], optional): Fields to return.
            Defaults to Query(None, alias="return").

    Returns:
        Dict: Results and pagination information
    """
    results = await search_cards(
        db=db,
        all=True,
        return_attr=return_attr,
        creator_user_id=creator_user_id,
        title=None,
        tags=None,
        frameworks=None,
        sort_by="_id",
        descending=True,
    )
    return results


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ModelCardModelDB,
    response_model_exclude_unset=True,
)
async def create_model_card_metadata(
    card: ModelCardModelIn,
    tasks: BackgroundTasks,
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
    user: TokenData = Depends(get_current_user),
) -> Dict:
    """Create model card metadata

    Args:
        card (ModelCardModelIn): Model card
        tasks (BackgroundTasks): Background tasks to run
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB connection.
            Defaults to Depends(get_db).
        user (TokenData, optional): User data. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 409 if model card already exists

    Returns:
        Dict: Model card metadata
    """
    # NOTE: After this, still need to submit inference engine
    db, mongo_client = db
    card.tags = list(set(card.tags))  # remove duplicates
    card.frameworks = list(set(card.frameworks))

    # Sanitize html
    card.markdown = preprocess_html(card.markdown)
    card.performance = preprocess_html(card.performance)

    card_dict: dict = jsonable_encoder(
        ModelCardModelDB(
            **card.dict(),
            creator_user_id=user.user_id or "unknown",
            model_id=uncased_to_snake_case(card.title),
            last_modified=datetime.datetime.now(),
            created=datetime.datetime.now(),
        ),
        by_alias=True,  # Convert snake_case to camelCase
    )
    async with await mongo_client.start_session() as session:
        try:
            async with session.start_transaction():
                await db["models"].insert_one(card_dict)
        except DuplicateKeyError as err:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Unable to add model with user and ID {card_dict['creatorUserId']}/{card_dict['modelId']} as the ID already exists.",
            ) from err
    tasks.add_task(
        delete_orphan_services
    )  # Delete preview services created during model create form
    return card_dict


@router.put(
    "/{creator_user_id}/{model_id}",
    response_model=ModelCardModelDB,
    response_model_exclude_unset=True,
)
async def update_model_card_metadata_by_id(
    model_id: str,
    creator_user_id: str,
    card: UpdateModelCardModel,
    tasks: BackgroundTasks,
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
    user: TokenData = Depends(get_current_user),
) -> Optional[Dict]:
    """Update model card metadata by ID

    Args:
        model_id (str): Model Id
        creator_user_id (str): Creator user id
        card (UpdateModelCardModel): Updated model card
        tasks (BackgroundTasks): Background tasks to run
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB connection.
            Defaults to Depends(get_db).
        user (TokenData, optional): User data. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 404 if model card does not exist
        HTTPException: 403 if user does not have permission to update model card

    Returns:
        Optional[Dict]: Updated model card metadata
    """
    tasks.add_task(
        delete_orphan_images
    )  # After update, check if any images were removed and sync with Minio
    db, mongo_client = db
    # by alias => convert snake_case to camelCase
    card_dict = {
        k: v for k, v in card.dict(by_alias=True).items() if v is not None
    }

    if "markdown" in card_dict:
        # Upload base64 encoded image to S3
        card_dict["markdown"] = preprocess_html(card_dict["markdown"])
    if "performance" in card_dict:
        card_dict["performance"] = preprocess_html(card_dict["performance"])

    if len(card_dict) > 0:
        card_dict["lastModified"] = str(datetime.datetime.now())
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
                elif existing_card["creatorUserId"] != user.user_id:
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
                        {"$set": card_dict},
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


@router.delete(
    "/{creator_user_id}/{model_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_model_card_by_id(
    model_id: str,
    creator_user_id: str,
    tasks: BackgroundTasks,
    db=Depends(get_db),
    user: TokenData = Depends(get_current_user),
):
    db, mongo_client = db
    async with await mongo_client.start_session() as session:
        async with session.start_transaction():
            # First, check that user actually has access
            existing_card = await db["models"].find_one(
                {"modelId": model_id, "creatorUserId": creator_user_id}
            )
            if (
                existing_card is not None
                and existing_card["creatorUserId"] != user.user_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have editor access to this model card",
                )
            await db["models"].delete_one(
                {"modelId": model_id, "creatorUserId": creator_user_id}
            )
    # https://stackoverflow.com/questions/6439416/status-code-when-deleting-a-resource-using-http-delete-for-the-second-time
    tasks.add_task(delete_orphan_images)  # Remove any related media
    tasks.add_task(delete_orphan_services)  # Remove any related services
