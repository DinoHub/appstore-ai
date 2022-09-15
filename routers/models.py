from typing import List, Mapping, Union, Optional

from clearml import Model, Task
from clearml.datasets import Dataset
from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from internal.clearml_client import clearml_client
from internal.db import db, mongo_client
from models.model import ModelCard

router = APIRouter()


@router.get("/models/")
async def get_models(length: Optional[int] = Query(default=None, ge=0)):
    # Get all models
    results = await db["models"].find().to_list(length=length)
    return JSONResponse(content=results, status_code=status.HTTP_200_OK)

@router.post("/models/", response_model=ModelCard, status_code=status.HTTP_201_CREATED)
async def create_model_card(card: ModelCard):
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
                detail="ClearML experiment not found.",
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
                    model = Model(model_id)
                    # NOTE: get_frameworks REST api will give ALL frameworks in project
                    # therefore, get them using Model object
                    card.model_details.text += (
                        f"{model.name}:\n\tFramework: {model.framework}\n"
                    )
                    card.tags.append(model.framework)
                except ValueError as e:
                    # Possibly model has been deleted
                    # TODO: Warn user that model metadata was not found
                    # NOTE: if they provided the inference url, should still be usable
                    continue  # thus, just ignore this
    card.tags = set(card.tags)  # remove duplicates
    card = jsonable_encoder(card)
    async with await mongo_client.start_session() as session:
        async with session.start_transaction():
            new_card = await db["models"].insert_one(card)
            created_card = await db["models"].find_one({"_id": new_card.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_card)
