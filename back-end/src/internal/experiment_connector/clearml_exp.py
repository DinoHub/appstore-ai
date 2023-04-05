"""ClearML experiment connector.
A interface to interact with ClearML experiments.
"""
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
        exp.output_url = task.get_output_log_web_page().replace("/output/log", "")
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
        return dict(self.task.get_parameters(cast=True) or {})

    @property
    def tags(self) -> List[str]:
        if not self.task:
            raise ValueError("Not currently connected to any experiments")
        return list(self.task.get_tags())

    @property
    def metrics(self) -> List[Dict]:
        if not self.task:
            raise ValueError("Not currently connected to any experiments")
        raw_data: Dict[str, Dict] = self.task.get_reported_scalars()
        return [self._to_plotly_json(name, data) for name, data in raw_data.items()]

    @property
    def artifacts(self) -> Dict[str, Artifact]:
        if not self.task:
            raise ValueError("Not currently connected to any experiments")
        artifacts: Dict[str, ClearMLArtifact] = self.task.artifacts
        output: Dict[str, Artifact] = {}
        for name, artifact in artifacts.items():
            output[name] = Artifact(
                artifactType=artifact.type,
                name=name,
                url=artifact.url,
                timestamp=str(artifact.timestamp),
                framework=None,
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
                    artifactType="model",
                    name=model.name,
                    url=model.url,
                    framework=model.framework,
                    timestamp=None,
                )
        return output

    @property
    def plots(self) -> List[Dict]:
        """Get all plots from the current experiment.

        Raises:
            ValueError: If not currently connected to any experiments

        Returns:
            List[Dict]: List of plotly json objects
        """
        if not self.task:
            raise ValueError("Not currently connected to any experiments")
        return [json.loads(plot["plot_str"]) for plot in self.task.get_reported_plots()]

    def get_metadata(self) -> Dict:
        """Get metadata for the current experiment.

        Raises:
            ValueError: If not currently connected to any experiments
            ValueError: If unable to find task

        Returns:
            Dict: Metadata for the current experiment
        """
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

    def clone_self(self, clone_name: Optional[str] = None) -> "ClearMLExperiment":
        """Clone the current experiment.

        Args:
            clone_name (Optional[str], optional): Name of cloned exp. Defaults to None.

        Raises:
            ValueError: If not currently connected to any experiments

        Returns:
            ClearMLExperiment: Cloned experiment
        """
        if not self.id:
            raise ValueError("Not currently connected to any experiments")
        task = Task.clone(source_task=self.id, name=clone_name)
        return task

    def execute(
        self,
        queue_name: Optional[str] = "default",
        queue_id: Optional[str] = None,
    ) -> Dict:
        """Add current experiment to the ClearML task queue.

        Args:
            queue_name (Optional[str], optional): Name of queue. Defaults to "default".
            queue_id (Optional[str], optional): ID of queue (in place of name). Defaults to None.

        Raises:
            ValueError: If not currently connected to any experiments

        Returns:
            Dict: An enqueue JSON response
        """
        if not self.task:
            raise ValueError("Not currently connected to any experiments")
        return dict(
            self.task.enqueue(self.task, queue_name=queue_name, queue_id=queue_id)
        )

    def close(self, delete_task: bool = False, delete_artifacts: bool = False) -> None:
        if not self.task:
            raise ValueError("Not currently connected to any experiments")
        self.task.close()
        if delete_task:
            self.delete(delete_artifacts=delete_artifacts)

    def delete(self, delete_artifacts: bool = False) -> bool:
        """Delete the current experiment.

        Args:
            delete_artifacts (bool, optional): If artifacts associated should also be deleted.
                Defaults to False.

        Raises:
            ValueError: If not currently connected to any experiments

        Returns:
            bool: If the experiment was successfully deleted
        """
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
        """List all experiments.

        Args:
            ids (Optional[List[str]], optional): Filter by list of exp ids. Defaults to None.
            project (Optional[str], optional): Filter by list of exp projects. Defaults to None.
            exp_name (Optional[str], optional): Filter by list of exp names. Defaults to None.
            tags (Optional[List[str]], optional): Filter by list of tags. Defaults to None.
            task_filter (Optional[Dict], optional): More filter and sort options. Defaults to None.

        Returns:
            List[Task]: List of experiments matching the filter
        """
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
        """Convert ClearML metrics data to plotly json.

        Args:
            title (str): Graph title
            data (Dict): ClearML metrics data

        Returns:
            Dict[str, Dict]: Plotly compatible json
        """
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
