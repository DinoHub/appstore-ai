from fastapi import APIRouter

from internal.clearml_client import clearml_client
from models.experiment import ClonePackage

router = APIRouter()


@router.get("/experiments/{id}")
async def get_experiment(id: str):
    exp_list = clearml_client.tasks.get_by_id(task=id)
    return {"id": exp_list.data.id, "name": exp_list.data.name, "rest": exp_list.data}


@router.post("/experiments/clone")
async def clone_exp(item: ClonePackage):
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
