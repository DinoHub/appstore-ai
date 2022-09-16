from typing import Dict
from fastapi import APIRouter

from internal.clearml_client import clearml_client
from models.experiment import ClonePackageModel

router = APIRouter(prefix="/experiments", tags=["Experiments"])


@router.get("/{id}")
async def get_experiment(id: str):
    exp_list = clearml_client.tasks.get_by_id(task=id)
    return {"id": exp_list.data.id, "name": exp_list.data.name, "rest": exp_list.data}


@router.post("/clone")
async def clone_experiment(item: ClonePackageModel):
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
async def edit_experiment_config(experiment_id: str, config: Dict):
    response = clearml_client.tasks.edit_configuration(
        configuration=config,
        task=experiment_id
    ) # response is an integer indicating success of update
    raise NotImplementedError
