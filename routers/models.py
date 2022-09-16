import json
import re
from typing import List, Mapping, Union

from bson import json_util
from clearml import Model, Task
from fastapi import APIRouter, HTTPException, status, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from internal.clearml_client import clearml_client
from internal.db import db, mongo_client
from models.model import (
    ModelCardModelDB,
    ModelCardModelIn,
    UpdateModelCardModel,
    FindModelCardModel,
)

router = APIRouter(prefix="/models")


@router.post("/search", response_model=ModelCardModelIn)
async def get_model_cards(query: FindModelCardModel):
    # Search model cards
    # TODO: Pagination support
    # NOTE: if nothing provided, return all
    # TODO: if possible, consider an option like elasticsearch or
    # mongodb atlas search to allow for fuzzy matching
    db_query = {
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
        db_query["title"] = (
            {
                # NOTE: not sure if security risk
                "$regex": re.escape(query.title),
                "$options": "i",
            },
        )
    if query.sort:
        # TODO: refactor this to be more intuitive
        query.sort = [
            (col_name, 1 if order == "ASC" else -1) for col_name, order in query.sort
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
async def get_model_card_by_id(model_id: str):
    # Get model card by database id (NOT clearml id)
    model = await db["models"].find_one({"_id": model_id})
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    model = json.loads(json_util.dumps(model))
    return JSONResponse(status_code=status.HTTP_200_OK, content=model)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_model_card(card: ModelCardModelIn):
    # If exp id is provided, some metadata can be obtained from ClearML
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
            card.performance = {"title": "Performance", "text": "", "media": []}
        card.performance.media.append(
            task.get_reported_scalars()
        )  # do not override existing plots
        # NOTE: switch to backend rest api as only that let's me get info on user
        # NOTE: we can only obtain attributes using "." notation from the data below
        task_data: Mapping[str, Union[str, Mapping]] = clearml_client.tasks.get_by_id(
            task=card.clearml_exp_id
        ).data
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
        async with session.start_transaction():
            new_card = await db["models"].insert_one(card)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=new_card.inserted_id
    )


@router.put("/{model_id}", response_model=ModelCardModelDB)
async def update_model_card_by_id(model_id: str, card: UpdateModelCardModel):
    # TODO: Check that user is the model owner
    card = {k: v for k, v in card.dict().items() if v is not None}

    if len(card) > 0:
        # perform transaction to ensure we can roll back changes
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                result = await db["models"].update_one(
                    {"_id": model_id}, {"$set": card}
                )

                if (
                    result.modified_count == 1
                ):  # NOTE: how pythonic is this? (seems to violate DRY)
                    # TODO: consider just removing the lines below
                    if (
                        updated_card := await db["models"].find_one({"_id": model_id})
                    ) is not None:
                        return updated_card
    # If no changes, try to return existing card
    if (existing_card := await db["models"].find_one({"_id": model_id})) is not None:
        return existing_card

    # Else, card never existed
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Model Card with ID: {model_id} not found.",
    )


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model_card_by_id(model_id: str):
    # TODO: Check that user is the owner of the model card
    async with await mongo_client.start_session() as session:
        async with session.start_transaction():
            await db["models"].delete_one({"_id": model_id})
    # https://stackoverflow.com/questions/6439416/status-code-when-deleting-a-resource-using-http-delete-for-the-second-time
    # TODO: Should actual model be deleted as well?

@router.post("/{model_id}/inference")
async def submit_test_inference(inference: UploadFile = File(description="Test samples for inference")):
    # TODO: send file to inference engine to get output
    # TODO: raise HTTP error if sample input invalid (let model handle)
    # TODO: then pipe output to HTML visualization engine

    # Finally, return the HTML

    raise NotImplementedError