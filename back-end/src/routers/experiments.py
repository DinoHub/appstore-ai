import logging
from typing import Dict

from clearml.backend_api.session.client import APIClient
from fastapi import APIRouter, Depends, HTTPException, status

from ..internal.dependencies.clearml_client import clearml_api_client
from ..internal.experiment_connector import Experiment
from ..models.experiment import (
    ClonePackageModel,
    Connector,
    ExperimentResponse,
)

router = APIRouter(prefix="/experiments", tags=["Experiments"])


@router.get("/{exp_id}", response_model=ExperimentResponse)
def get_experiment(
    exp_id: str,
    connector: Connector,
    return_plots: bool = True,
    return_artifacts: bool = True,
) -> Dict:
    """Get experiment by ID.

    Args:
        exp_id (str): Experiment ID
        connector (Connector): Connector to use
        return_plots (bool, optional): If plots should be returned. Defaults to True.
        return_artifacts (bool, optional): If artifacts should be returned. Defaults to True.

    Raises:
        HTTPException: 404 Not Found if experiment does not exist
        HTTPException: 500 Internal Server Error if error occurs

    Returns:
        Dict: Experiment details
    """
    try:
        exp = Experiment.from_connector(connector).get(exp_id=exp_id)
        # Extract framework from models
        frameworks = set()
        for model in exp.models.values():
            frameworks.add(model.framework)

        data = {
            "id": exp.id,
            "name": exp.exp_name,
            "output_url": exp.output_url,
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
            data["artifacts"] = {}
            data["artifacts"].update(exp.artifacts)
            data["artifacts"].update(exp.models)
        return data
    except ValueError as err:
        logging.error(err)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with ID {exp_id} not found.",
        ) from err
    except Exception as err:
        logging.error(err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting experiment with ID {exp_id}.",
        ) from err


@router.post("/clone")
def clone_experiment(
    item: ClonePackageModel,
    connector: Connector,
) -> Dict:
    """Clone experiment. (Not implemented yet.)

    Args:
        item (ClonePackageModel): Item to clone
        connector (Connector): Experiment connector

    Returns:
        Dict: Details of cloned experiment
    """
    # TODO: Use this for transfer learning if required?
    exp = Experiment.from_connector(connector).get(exp_id=item.id)
    if item.clone_name is None or item.clone_name == "":
        new_exp = exp.clone_self(clone_name=f"Clone of {exp.exp_name}")
    else:
        new_exp = exp.clone_self(clone_name=f"{item.clone_name}")
    cloned = Experiment.from_connector(connector).get(exp_id=new_exp.id)
    return {
        "id": exp.id,
        "name": exp.exp_name,
        "clone_id": cloned.id,
        "clone_name": cloned.exp_name,
    }


# @router.put("/config/{experiment_id}")
# def edit_experiment_config(
#     experiment_id: str,
#     config: Dict,
#     clearml_client: APIClient = Depends(clearml_api_client),
# ) :
#     response = clearml_client.tasks.edit_configuration(
#         configuration=config, task=experiment_id
#     )  # response is an integer indicating success of update
#     raise NotImplementedError
