import json
import re
import tempfile
from typing import BinaryIO, List, Mapping, Optional, Union

import filetype
import httpx
from bson import ObjectId, json_util
from clearml import Model, Task
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse
from pymongo.errors import DuplicateKeyError

from ..internal.clearml_client import clearml_client
from ..internal.db import get_db
from ..internal.file_validator import (
    MaxFileSizeException,
    MaxFileSizeValidator,
    ValidateFileUpload,
)
from ..internal.inference import process_inference_data, stream_response
from ..models.engine import IOTypes
from ..models.model import (
    FindModelCardModel,
    InferenceEngine,
    ModelCardModelDB,
    ModelCardModelIn,
    UpdateModelCardModel,
)

CHUNK_SIZE = 1024
BytesPerGB = 1024 * 1024 * 1024
MAX_UPLOAD_SIZE_GB = 1

MEDIA_IO_TYPES = {IOTypes.Media, IOTypes.Generic}

TEXT_IO_TYPES = {IOTypes.Generic, IOTypes.JSON, IOTypes.Text}

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
    max_upload_size=MAX_UPLOAD_SIZE_GB * BytesPerGB
)
router = APIRouter(prefix="/models", tags=["Models"])


@router.post("/search", response_model=ModelCardModelIn)
async def get_model_cards(query: FindModelCardModel, db=Depends(get_db)):
    # Search model cards
    # TODO: Pagination support
    # NOTE: if nothing provided, return all
    # TODO: if possible, consider an option like elasticsearch or
    # mongodb atlas search to allow for fuzzy matching
    db, _ = db
    db_query = {
        "model_id": query.model_id,
        "task": query.task,
        "owner": query.owner,
        "creator": query.creator,
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


@router.get("/{model_id}")
async def get_model_card_by_id(model_id: str, db=Depends(get_db)):
    db, _ = db
    # Get model card by database id (NOT clearml id)
    model = await db["models"].find_one({"model_id": model_id})
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    model = json.loads(json_util.dumps(model))
    return JSONResponse(status_code=status.HTTP_200_OK, content=model)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_model_card_metadata(
    card: ModelCardModelIn, db=Depends(get_db)
):
    # NOTE: After this, still need to submit inference engine
    # TODO: Endpoint for submit inference engine
    # If exp id is provided, some metadata can be obtained from ClearML
    db, mongo_client = db
    if card.clearml_exp_id:
        # Retrieve metadata from ClearML experiment
        # Get Scalars if present
        # this data will be passed to front end (Plotly.js)
        # OR we can create plots within here and save the image to db
        # NOTE: I specifically use clearml sdk as it is the only way to get the data points
        # backend rest api does not expose this info (only summary statistics)
        try:
            task = Task.get_task(task_id=card.clearml_exp_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ClearML experiment with id {card.clearml_exp_id} not found.",
            )
        if card.performance is None:
            card.performance = {
                "title": "Performance",
                "text": "",
                "media": [],
            }
        card.performance.media.append(
            task.get_reported_scalars()
        )  # do not override existing plots
        # NOTE: switch to backend rest api as only that let's me get info on user
        # NOTE: we can only obtain attributes using "." notation from the data below
        task_data: Mapping[
            str, Union[str, Mapping]
        ] = clearml_client.tasks.get_by_id(task=card.clearml_exp_id).data
        # NOTE: I can only get user id, not the name
        # NOTE: consider using userid to form a url to the user account
        card.creator = task_data.user
        card.tags.extend(task_data.tags)
        # Start by getting model id so that we can get them
        # NOTE: client api from testing seems to only give id and name if I use th
        # this is why I don't just use the get_all REST api
        output_models: List[Mapping[str, str]] = task_data.models.output
        # Obtain Id
        # Use set as there can be duplicate model ids as some files refer to same model
        model_ids = set(map(lambda model: model.model, output_models))
        if card.model_details is None:
            card.model_details = {"title": "Model Details", "text": ""}
        # For each model,
        if len(model_ids) > 0:
            # potentially a script could output multiple models
            for model_id in model_ids:
                try:
                    # NOTE: get_frameworks REST api will give ALL frameworks in project
                    # therefore, get them using Model object
                    card.frameworks.append(Model(model_id).framework)
                except ValueError as e:
                    # Possibly model has been deleted
                    # TODO: Warn user that model metadata was not found
                    # NOTE: if they provided the inference url, should still be usable
                    continue  # thus, just ignore this
    card.tags = set(card.tags)  # remove duplicates
    card.frameworks = set(
        card.frameworks
    )  # TODO: Decide if frameworks should be singular (i.e. only one framework allowed)
    card = jsonable_encoder(ModelCardModelDB(**card.dict()))
    async with await mongo_client.start_session() as session:
        try:
            async with session.start_transaction():
                new_card = await db["models"].insert_one(card)
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unable to add model with ID {card['model_id']} as the ID already exists.",
            )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=new_card.inserted_id
    )


@router.put("/{model_id}", response_model=ModelCardModelDB)
async def update_model_card_metadata_by_id(
    model_id: str, card: UpdateModelCardModel, db=Depends(get_db)
):
    db, mongo_client = db
    # TODO: Check that user is the model owner
    card = {k: v for k, v in card.dict().items() if v is not None}
    # TODO: should we consider updating datetime to current datetime??

    if len(card) > 0:
        # perform transaction to ensure we can roll back changes
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                result = await db["models"].update_one(
                    {"model_id": model_id}, {"$set": card}
                )

                if (
                    result.modified_count == 1
                ):  # NOTE: how pythonic is this? (seems to violate DRY)
                    # TODO: consider just removing the lines below
                    if (
                        updated_card := await db["models"].find_one(
                            {"model_id": model_id}
                        )
                    ) is not None:
                        return updated_card
    # If no changes, try to return existing card
    if (
        existing_card := await db["models"].find_one({"model_id": model_id})
    ) is not None:
        print("Nothing modified")
        return existing_card

    # TODO: Might need to update inference engine

    # Else, card never existed
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Model Card with ID: {model_id} not found.",
    )


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model_card_by_id(model_id: str, db=Depends(get_db)):
    # TODO: Check that user is the owner of the model card
    db, mongo_client = db
    async with await mongo_client.start_session() as session:
        async with session.start_transaction():
            await db["models"].delete_one({"model_id": model_id})
    # https://stackoverflow.com/questions/6439416/status-code-when-deleting-a-resource-using-http-delete-for-the-second-time
    # TODO: Should actual model be deleted as well?


@router.post("/inference/{model_id}", dependencies=[Depends(file_validator)])
async def make_test_inference(
    model_id: str,
    # media: Optional[List[UploadFile]] = File(None),
    # text: Optional[str] = Form(None),
    request: Request,
    db=Depends(get_db),
):
    # Get metadata of inference engine url
    media, text = await process_inference_data(request)
    # NOTE: we do not give error for empty input as some models
    # may not require any inputs

    # Get metadata about the inference engine of the model
    db, _ = db
    model = await db["models"].find_one(
        {
            "model_id": model_id,
        },
        projection=["inference_engine"],
    )
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with ID {model_id} not found.",
        )
    if "inference_engine" not in model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with ID {model_id} does not have known inference engine.",
        )
    engine: InferenceEngine = model["inference_engine"]
    inference_url = engine["service_url"]
    input_type = engine["input_schema"]

    # Validate File Size
    file_size_validator = MaxFileSizeValidator(MAX_UPLOAD_SIZE_GB * BytesPerGB)
    if input_type in MEDIA_IO_TYPES:
        for files in media:
            file: BinaryIO
            content_type: str
            for (_, (_, file, content_type)) in files:
                with tempfile.NamedTemporaryFile() as f:
                    try:
                        while content := file.read(CHUNK_SIZE):
                            file_size_validator(content)
                            f.write(content)
                        guessed_content_type = filetype.guess_mime(f.name)
                        if guessed_content_type not in ACCEPTED_CONTENT_TYPES:
                            raise ValueError
                        if content_type != content_type:  # MIME type mismatch
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"MIME Type Mismatch. Content type reported was {content_type}, but file was {guessed_content_type}",
                            )
                    except MaxFileSizeException:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File uploaded is too large. Limit is {MAX_UPLOAD_SIZE_GB}GB",
                        )
                    except ValueError:
                        raise HTTPException(
                            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            detail=f"File type {content_type} not supported",
                        )
                file.seek(
                    0
                )  # Set pointer to start of file to ensure file can be re-read

    return StreamingResponse(
        content=stream_response(
            media=media,
            text=text,
            url=inference_url + "/predict",
        ),
    )
