from msilib.schema import Error
from typing import Dict

from clearml.backend_api.session.client import APIClient
from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import JSONResponse, Response

from ..internal.clearml_client import clearml_api_client
from ..internal.experiment_connector import Experiment
from ..models.experiment import ClonePackageModel, Connector

router = APIRouter(prefix="/experiments", tags=["Experiments"])


@router.get("/{exp_id}")
async def get_experiment(
    exp_id: str,
    connector: Connector,
    return_plots: bool = True,
    return_artifacts: bool = True,
):
    try:
        exp = Experiment(connector).get(exp_id=exp_id)
        # Extract framework from models
        frameworks = set()
        for model in exp.models.values():
            frameworks.add(model.framework)

        data = {
            "id": exp.id,
            "name": exp.exp_name,
            "project_name": exp.project_name,
            "tags": exp.tags,
            "frameworks": list(frameworks),
            "config": exp.config,
            "owner": exp.user,
        }

        if return_plots:
            # scalars are raw data logged during exp
            data["scalars"] = exp.metrics
            # plots are already plotly compatible
            data["plots"] = exp.plots

        if return_artifacts:
            print(exp.artifacts)
            print(exp.models)
            data["artifacts"] = {}
            data["artifacts"].update(exp.artifacts)
            data["artifacts"].update(exp.models)

        return data
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=e,
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=f"Error"
        )


@router.post("/clone")
async def clone_experiment(
    item: ClonePackageModel,
    clearml_client: APIClient = Depends(clearml_api_client),
):
    exp_list = clearml_client.tasks.get_by_id(task=item.id)
    if item.clone_name == None:
        new_exp = exp_list.clone(new_task_name=f"Clone of {exp_list.data.name}")
    else:
        new_exp = exp_list.clone(new_task_name=f"{item.clone_name}")
    cloned = clearml_client.tasks.get_by_id(task=new_exp.id)
    return {
        "id": exp_list.data.id,
        "name": exp_list.data.name,
        "clone_id": cloned.data.id,
        "clone_name": cloned.data.name,
    }


@router.put("/config/{experiment_id}")
async def edit_experiment_config(
    experiment_id: str,
    config: Dict,
    clearml_client: APIClient = Depends(clearml_api_client),
):
    response = clearml_client.tasks.edit_configuration(
        configuration=config, task=experiment_id
    )  # response is an integer indicating success of update
    raise NotImplementedError
