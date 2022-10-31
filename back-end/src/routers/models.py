import datetime
import json
import re

import httpx
from bson import json_util
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError

from ..config.config import config
from ..internal.auth import get_current_user
from ..internal.db import get_db
from ..internal.file_validator import ValidateFileUpload
from ..internal.utils import uncased_to_snake_case
from ..models.iam import User
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


# TODO: Convert this to GET
@router.post("/search", response_model=ModelCardModelIn)
async def get_model_cards(query: FindModelCardModel, db=Depends(get_db)):
    # Search model cards
    # TODO: Pagination support
    # NOTE: if nothing provided, return all
    # TODO: if possible, consider an option like elasticsearch or
    # mongodb atlas search to allow for fuzzy matching
    db, _ = db
    db_query = {
        "modelId": query.model_id,
        "task": query.task,
        "creatorUserId": query.creator_user_id,
        "owner": query.owner,
        "pointOfContact": query.point_of_contact,
        "tags": {
            # NOTE: assumes AND
            "$all": query.tags
        },
        "frameworks": {"$in": query.frameworks},
    }
    if query.title:
        db_query["title"] = {
            # NOTE: not sure if security risk
            # escape so that chars like / are accepted in title
            "$regex": re.escape(query.title),
            "$options": "i",
        }

    if query.sort:
        # TODO: refactor this to be more intuitive
        query.sort = [
            (col_name, 1 if order == "ASC" else -1)
            for col_name, order in query.sort
        ]
    # Remove empty attributes
    if not query.tags:
        del db_query["tags"]
    if not query.frameworks:
        del db_query["frameworks"]
    # If user only wants some attrs to be returned (e.g. summary card only needs some attributes)
    db_projection = query.return_attrs
    db_query = {k: v for k, v in db_query.items() if v is not None}
    results = (
        await db["models"]
        .find(filter=db_query, projection=db_projection, sort=query.sort)
        .to_list(length=None)
    )
    results = json.loads(
        json_util.dumps(results)
    )  # enable bson from mongodb to be converted to json
    return JSONResponse(content=results, status_code=status.HTTP_200_OK)


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
    user: User = Depends(get_current_user),
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
    user: User = Depends(get_current_user),
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
    user: User = Depends(get_current_user),
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


# @router.post("/inference/{model_id}", dependencies=[Depends(file_validator)])
# async def make_test_inference(
#     model_id: str,
#     request: Request,
#     media: Optional[List[UploadFile]] = File(
#         None,
#         description="Default file field to store media file in. Note that additional media fields can be sent to this endpoint.",
#     ),
#     text: Optional[str] = Form(
#         None,
#         description="Input to this is expected to be formatted as a JSON. Default form field to store text/json in. Note that additional form fields can be sent to this endpoint.",
#     ),
#     db=Depends(get_db),
# ):
#     # NOTE: Deprecated in Favour of Gradio
#     raise DeprecationWarning("Deprecated in favour of Gradio")
#     # TODO: Consider if we can simply just return
#     # the url to the front end and let the front-
#     # end directly call the service
#     # PRO: faster, more reliable
#     # CON: potential issue if the service not publicly accessible
#     # (e.g private service) as then only the back-end can access
#     # it
#     # Get metadata of inference engine url
#     media_data, json_data = await process_inference_data(request)
#     # NOTE: we do not give error for empty input as some models
#     # may not require any inputs

#     # Get metadata about the inference engine of the model
#     db, _ = db
#     model = await db["models"].find_one(
#         {
#             "model_id": model_id,
#         },
#         projection=["inference_engine"],
#     )
#     if model is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Model with ID {model_id} not found.",
#         )
#     if "inference_engine" not in model:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Model with ID {model_id} does not have known inference engine.",
#         )
#     engine: InferenceEngine = model["inference_engine"]
#     inference_url = engine["service_url"]
#     input_interface = engine["input_schema"]["io_type"]

#     # Validate File Size
#     file_size_validator = MaxFileSizeValidator(
#         config.MAX_UPLOAD_SIZE_GB * BytesPerGB
#     )
#     if input_interface in MEDIA_IO_INTERFACES:
#         for files in media_data:
#             file: BinaryIO
#             content_type: str
#             for (_, (_, file, content_type)) in files:
#                 with tempfile.NamedTemporaryFile() as f:
#                     try:
#                         while content := file.read(CHUNK_SIZE):
#                             file_size_validator(content)
#                             f.write(content)
#                         guessed_content_type = filetype.guess_mime(f.name)
#                         if guessed_content_type not in ACCEPTED_CONTENT_TYPES:
#                             raise ValueError
#                         if content_type != content_type:  # MIME type mismatch
#                             raise HTTPException(
#                                 status_code=status.HTTP_400_BAD_REQUEST,
#                                 detail=f"MIME Type Mismatch. Content type reported was {content_type}, but file was {guessed_content_type}",
#                             )
#                     except MaxFileSizeException:
#                         raise HTTPException(
#                             status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
#                             detail=f"File uploaded is too large. Limit is {config.MAX_UPLOAD_SIZE_GB}GB",
#                         )
#                     except ValueError:
#                         raise HTTPException(
#                             status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
#                             detail=f"File type {content_type} not supported",
#                         )
#                 file.seek(
#                     0
#                 )  # Set pointer to start of file to ensure file can be re-read
#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             f"{inference_url}/predict",
#             files=media_data,
#             data=json_data,
#             timeout=MAKE_REQUEST_INFERENCE_TIMEOUT,
#         )
#         try:
#             response.raise_for_status()
#         except httpx.HTTPStatusError as e:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Error when calling inference engine: {e}",
#             )
#         return StreamingResponse(
#             BytesIO(response.content),
#             media_type=response.headers.get("Content-Type"),
#         )
# return stream_generator(inference_url, media_data, json_data)
# TODO: Streaming generator that will also attempt
# to get a media type
# stream = (
#     await httpx.AsyncClient()
#     .stream("POST", f"{inference_url}/predict", files=media, data=text)
#     .__aenter__()
# ) # manually open stream context
# # this allows us to first get the MIME type of the output
# media_type = stream.headers.get("Content-Type")
# return StreamingResponse(
#     content=stream.aiter_raw(), media_type=media_type
# aiter_raw automatically closes the stream when consumed
