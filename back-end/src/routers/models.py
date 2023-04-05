import datetime
import json
import re
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from bson import json_util
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError

from ..config.config import config
from ..internal.auth import get_current_user, check_is_admin
from ..internal.dependencies.file_validator import ValidateFileUpload
from ..internal.dependencies.minio_client import (
    get_presigned_url,
    minio_api_client,
)
from ..internal.dependencies.mongo_client import get_db
from ..internal.experiment_connector import Experiment
from ..internal.preprocess_html import (
    preprocess_html_get,
    preprocess_html_post,
)
from ..internal.tasks import (
    delete_orphan_images,
    delete_orphan_services,
    export_selected_models,
)
from ..internal.utils import uncased_to_snake_case
from ..models.iam import TokenData
from ..models.model import (
    GetFilterResponseModel,
    ModelCardModelDB,
    ModelCardModelIn,
    SearchModelResponse,
    UpdateModelCardModel,
    ModelCardPackage,
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


@router.get("/{creator_user_id}/{model_id}")
async def get_model_card_by_id(
    model_id: str,
    creator_user_id: str,
    convert_s3: bool = Query(default=True),
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
    s3_client=Depends(minio_api_client),
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
    # Get HTML and Video Sources, replace URLs with signed URLs
    # this is done if S3 bucket is private (e.g secure deployment)
    # and thus we need user credentials to view images and videos
    # stored on s3
    if convert_s3:
        # Get HTML
        try:
            model["markdown"] = await preprocess_html_get(model["markdown"])
            model["performance"] = await preprocess_html_get(model["performance"])
        except Exception as err:
            print(f"Error: {err}")
        if "videoLocation" in model and model["videoLocation"] is not None:
            try:
                url: str = model["videoLocation"]
                url = url.removeprefix("s3://")
                bucket, object_name = url.split("/", 1)
                model["videoLocation"] = await get_presigned_url(
                    s3_client, object_name, bucket
                )
            except Exception as err:
                print(f"Error: {err}")
                model["videoLocation"] = None
    return model


@router.get("/", response_model=SearchModelResponse, response_model_exclude_unset=True)
async def search_cards(
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
    page: int = Query(default=1, alias="p", gt=0),
    rows_per_page: int = Query(default=10, alias="n", ge=0),
    descending: bool = Query(default=False, alias="desc"),
    sort_by: str = Query(default="_id", alias="sort"),
    generic_search_text: Optional[str] = Query(default=None, alias="genericSearchText"),
    title: Optional[str] = Query(default=None),
    tasks: Optional[List[str]] = Query(default=None, alias="tasks[]"),
    tags: Optional[List[str]] = Query(default=None, alias="tags[]"),
    frameworks: Optional[List[str]] = Query(default=None, alias="frameworks[]"),
    creator_user_id: Optional[str] = Query(default=None, alias="creator"),
    creator_user_id_partial: Optional[str] = Query(
        default=None, alias="creatorUserIdPartial"
    ),
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
        generic_search_text (Optional[str], optional): Search through any relevant text fields. Defaults to Query(default=None, alias="genericSearchText").
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
    # TODO: This is a really stupid way to do search
    # so should prob rely on elasticsearch or something
    # So set up ES, sync with Mongo with Logstash, then
    # use ES BM25 search
    if generic_search_text:
        query["$or"] = [
            {
                "title": {
                    "$regex": re.escape(generic_search_text),
                    "$options": "i",
                }
            },
            {
                "task": {
                    "$regex": re.escape(generic_search_text),
                    "$options": "i",
                }
            },
            {
                "tags": {
                    "$regex": re.escape(generic_search_text),
                    "$options": "i",
                }
            },
            {
                "frameworks": {
                    "$regex": re.escape(generic_search_text),
                    "$options": "i",
                }
            },
            {
                "creatorUserId": {
                    "$regex": re.escape(generic_search_text),
                    "$options": "i",
                }
            },
            {
                "owner": {
                    "$regex": re.escape(generic_search_text),
                    "$options": "i",
                }
            },
            {
                "pointOfContact": {
                    "$regex": re.escape(generic_search_text),
                    "$options": "i",
                }
            },
            {
                "markdown": {
                    "$regex": re.escape(generic_search_text),
                    "$options": "i",
                }
            },
            {
                "performance": {
                    "$regex": re.escape(generic_search_text),
                    "$options": "i",
                }
            },
            {
                "description": {
                    "$regex": re.escape(generic_search_text),
                    "$options": "i",
                }
            },
            {
                "explanation": {
                    "$regex": re.escape(generic_search_text),
                    "$options": "i",
                }
            },
            {
                "usage": {
                    "$regex": re.escape(generic_search_text),
                    "$options": "i",
                }
            },
            {
                "limitations": {
                    "$regex": re.escape(generic_search_text),
                    "$options": "i",
                }
            },
        ]

    if title:
        query["title"] = {"$regex": re.escape(title), "$options": "i"}
    if tasks:
        query["task"] = {"$in": [re.compile(task, re.IGNORECASE) for task in tasks]}
    if tags:
        query["tags"] = {"$all": [re.compile(tag, re.IGNORECASE) for tag in tags]}
    if frameworks:
        query["frameworks"] = {
            "$in": [re.compile(framework, re.IGNORECASE) for framework in frameworks]
        }
    if creator_user_id:
        query["creatorUserId"] = creator_user_id
    if creator_user_id_partial:
        query["creatorUserId"] = {
            "$regex": re.escape(creator_user_id_partial),
            "$options": "i",
        }
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

    # Ensure unique model ID
    # Note that ModelCardModelDB will further sanitize this
    # Limit length to max size of 64
    model_id = f"{uncased_to_snake_case(card.title)}-{uuid4()}"[:64]

    # Process tags and frameworks
    card.tags = list(set(card.tags))  # remove duplicates
    card.frameworks = list(set(card.frameworks))

    # Sanitize html
    card.markdown = await preprocess_html_post(card.markdown)
    card.performance = await preprocess_html_post(card.performance)
    if card.experiment.connector != "" and card.experiment.connector is not None:
        card.experiment.output_url = (
            Experiment.from_connector(card.experiment.connector)
            .get(exp_id=card.experiment.experiment_id)
            .output_url
        )
    card_dict: dict = jsonable_encoder(
        ModelCardModelDB(
            **card.dict(),
            creator_user_id=user.user_id or "unknown",
            model_id=model_id,
            last_modified=str(datetime.datetime.now()),
            created=str(datetime.datetime.now()),
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
    response_model=Optional[ModelCardModelDB],
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
    card_dict = {k: v for k, v in card.dict(by_alias=True).items() if v is not None}
    if "experiment" in card_dict:
        if card_dict["experiment"]["connector"] == "":
            card_dict["experiment"]["outputUrl"] = None
        else:
            card_dict["experiment"]["outputUrl"] = (
                Experiment.from_connector(card_dict["experiment"]["connector"])
                .get(exp_id=card_dict["experiment"]["experimentId"])
                .output_url
            )
    if "markdown" in card_dict:
        # Upload base64 encoded image to S3
        card_dict["markdown"] = await preprocess_html_post(card_dict["markdown"])
    if "performance" in card_dict:
        card_dict["performance"] = await preprocess_html_post(card_dict["performance"])
    if "task" in card_dict:
        if card_dict["task"] == "Reinforcement Learning":
            card_dict["inferenceServiceName"] = None
        else:
            card_dict["videoLocation"] = None

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
                elif (
                    existing_card["creatorUserId"] != user.user_id
                    and user.role != "admin"
                ):
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


@router.delete("/{creator_user_id}/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model_card_by_id(
    model_id: str,
    creator_user_id: str,
    tasks: BackgroundTasks,
    db=Depends(get_db),
    user: TokenData = Depends(get_current_user),
):
    """Delete model card by composite key of Creator User ID and Model ID

    Args:
        model_id (str): Model Id
        creator_user_id (str): Creator user id
        card (UpdateModelCardModel): Updated model card
        tasks (BackgroundTasks): Background tasks to run
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB connection.
            Defaults to Depends(get_db).
        user (TokenData, optional): User data. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 500 if arbitrary error occurs
    """
    try:
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
                    and user.role != "admin"
                ):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="User does not have editor access to this model card",
                    )
                await db["models"].delete_one(
                    {"modelId": model_id, "creatorUserId": creator_user_id}
                )
    except HTTPException as err:
        raise err
    except Exception as err:
        print("failed")
        print("Error: ", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Removal failed",
        ) from err
    # https://stackoverflow.com/questions/6439416/status-code-when-deleting-a-resource-using-http-delete-for-the-second-time
    tasks.add_task(delete_orphan_images)  # Remove any related media
    tasks.add_task(delete_orphan_services)  # Remove any related services


@router.delete("/multi", status_code=status.HTTP_204_NO_CONTENT)
async def delete_multiple_model_cards(
    card_package: ModelCardPackage,
    tasks: BackgroundTasks,
    db=Depends(get_db),
    user: TokenData = Depends(get_current_user),
):
    """Delete multiple model cards by List of composite keys of Creator User ID and Model ID

    Args:
        card_package (ModelCardPackage): List of Dictionaries containing models with composite ID identifiers to be removed
        card (UpdateModelCardModel): Updated model card
        tasks (BackgroundTasks): Background tasks to run
        db (Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient], optional): MongoDB connection.
            Defaults to Depends(get_db).
        user (TokenData, optional): User data. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 500 if arbitrary error occurs
    """
    try:
        db, mongo_client = db
        pkg = card_package.dict()["card_package"]
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                for x in pkg:
                    # First, check that user actually has access
                    existing_card = await db["models"].find_one(
                        {
                            "modelId": x["model_id"],
                            "creatorUserId": x["creator_user_id"],
                        }
                    )
                    if existing_card is not None and user.role != "admin":
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="User does not have editor access to this model card",
                        )
                    await db["models"].delete_one(
                        {
                            "modelId": x["model_id"],
                            "creatorUserId": x["creator_user_id"],
                        }
                    )
    except HTTPException as err:
        raise err
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Removal failed",
        ) from err
    # https://stackoverflow.com/questions/6439416/status-code-when-deleting-a-resource-using-http-delete-for-the-second-time
    tasks.add_task(delete_orphan_images)  # Remove any related media
    tasks.add_task(delete_orphan_services)  # Remove any related services


@router.post(
    "/export",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(check_is_admin)],
)
async def export_models(
    card_package: ModelCardPackage,
    tasks: BackgroundTasks,
    user: TokenData = Depends(get_current_user),
):
    """Export selected models in app store to S3 storage that can be imported to app store elsewhere

    Args:
        card_package (ModelCardPackage): List of Dictionaries containing models with composite ID identifiers to be removed
        tasks (BackgroundTasks): Background tasks to run
        user (TokenData, optional): User data. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 403 if user does not have admin/elevated privileges
        HTTPException: 500 if arbitrary error occurs
    """
    try:
        if user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have sufficient privilege to export models!",
            )
        else:
            tasks.add_task(export_selected_models, card_package, user)
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server ran into an unexpected error",
        )
