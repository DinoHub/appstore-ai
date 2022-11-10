import json
from typing import Dict, List, Optional

from clearml import Model, Task
from clearml.task import Artifact as ClearMLArtifact

from ...models.model import Artifact
from .connector import ExperimentConnector


class ClearMLExperiment(ExperimentConnector):
    def __init__(self):
        super().__init__()
        self.task: Optional[Task] = None

    @classmethod
    def get(
        cls,
        exp_id: Optional[str] = None,
        project: Optional[str] = None,
        exp_name: Optional[str] = None,
    ) -> "ClearMLExperiment":
        exp = cls()
        if exp_id:
            task: Task = Task.get_task(task_id=exp_id)
        elif project and exp_name:
            task = Task.get_task(project_name=project, task_name=exp_name)
        else:
            raise ValueError("Must specify either exp_id or project and exp_name")
        exp.id = task.id
        exp.project_name = task.get_project_name()
        exp.exp_name = task.name
        exp.task = task
        metadata = exp.get_metadata()
        exp.user = metadata["user"]

        return exp

    @classmethod
    def clone(
        cls, exp_id: str, clone_name: Optional[str] = None
    ) -> "ClearMLExperiment":
        task = Task.clone(source_task=exp_id, name=clone_name)
        exp = cls()
        exp.id = task.id
        exp.project_name = task.get_project_name()
        exp.exp_name = task.name
        exp.task = task
        return exp

    @property
    def config(self) -> Dict:
        if not self.task:
            raise ValueError("Not currently connected to any experiments")
        return self.task.get_parameters(cast=True)

    @property
    def tags(self) -> List:
        if not self.task:
            raise ValueError("Not currently connected to any experiments")
        return self.task.get_tags()

    @property
    def metrics(self) -> List[Dict]:
        if not self.task:
            raise ValueError("Not currently connected to any experiments")
        raw_data: Dict[str, Dict] = self.task.get_reported_scalars()
        return list(
            map(lambda x: self._to_plotly_json(x[0], x[1]), raw_data.items())
        )

    @property
    def artifacts(self) -> Dict[str, Artifact]:
        if not self.task:
            raise ValueError("Not currently connected to any experiments")
        artifacts: Dict[str, ClearMLArtifact] = self.task.artifacts
        output: Dict[str, Artifact] = {}
        for name, artifact in artifacts.items():
            output[name] = Artifact(
                artifact_type=artifact.type,
                name=name,
                url=artifact.url,
                timestamp=artifact.timestamp,
            )
        return output

    @property
    def models(self) -> Dict[str, Artifact]:
        if not self.task:
            raise ValueError("Not currently connected to any experiments")

        models: Dict[str, List[Model]] = self.task.get_models()
        output: Dict[str, Artifact] = {}
        for values in models.values():
            # model_type: "input", "output"
            for model in values:
                output[model.name] = Artifact(
                    artifact_type="model",
                    name=model.name,
                    url=model.url,
                    framework=model.framework,
                )
        return output

    @property
    def plots(self) -> List[Dict]:
        if not self.task:
            raise ValueError("Not currently connected to any experiments")
        # NOTE: Plot data is plotly compatible
        # TODO: Consider using back end to GET this info, and front-end editor
        # add option to import the plot, giving options based on the
        # results of the GET request for plot and scalar info
        return list(
            map(
                lambda x: json.loads(x["plot_str"]),
                self.task.get_reported_plots(),
            )
        )

    def get_metadata(self) -> Dict:
        if not self.task:
            raise ValueError("Not currently connected to any experiments")
        tasks = Task.query_tasks(
            project_name=self.project_name,
            task_name=self.exp_name,
            tags=self.tags,
            additional_return_fields=["user"],
        )
        if len(tasks) == 0:
            raise ValueError("Unable to find task")
        return tasks[0]

    def clone(self, clone_name: Optional[str] = None) -> "ClearMLExperiment":
        if not self.id:
            raise ValueError("Not currently connected to any experiments")
        task = Task.clone(source_task=self.id, name=clone_name)
        return task

    def execute(
        self,
        queue_name: Optional[str] = "default",
        queue_id: Optional[str] = None,
    ) -> Dict:
        if not self.task:
            raise ValueError("Not currently connected to any experiments")
        return self.task.enqueue(queue_name=queue_name, queue_id=queue_id)

    def close(self, delete_task: bool = False, delete_artifacts: bool = False) -> None:
        if not self.task:
            raise ValueError("Not currently connected to any experiments")
        self.task.close()
        if delete_task:
            self.delete(delete_artifacts=delete_artifacts)

    def delete(self, delete_artifacts: bool = False) -> bool:
        if not self.task:
            raise ValueError("Not currently connected to any experiments")
        return self.task.delete(delete_artifacts_and_models=delete_artifacts)

    @staticmethod
    def list_tasks(
        ids: Optional[List[str]] = None,
        project: Optional[str] = None,
        exp_name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        task_filter: Optional[Dict] = None,
    ) -> List[Task]:
        task_list = Task.get_tasks(
            task_ids=ids,
            project_name=project,
            task_name=exp_name,
            tags=tags,
            task_filter=task_filter,
        )
        return task_list

    @staticmethod
    def _to_plotly_json(title: str, data: Dict) -> Dict[str, Dict]:
        result = {
            "data": [],
            "layout": {
                "title": title,
            },
        }
        for values in data.values():
            result["data"].append(
                {
                    "mode": "lines+markers",
                    **values,
                }
            )
        return result
