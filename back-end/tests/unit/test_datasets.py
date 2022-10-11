from pathlib import Path

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from src.internal.data_connector import ClearMLDataset


def test_get_all_datasets(
    client: TestClient,
):
    response = client.post("/datasets/search", json={})
    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response_json, list)
    # might be more than 2 if fail to clean up test
    assert len(response_json) >= 2


@pytest.mark.parametrize(
    "project",
    [
        "ClearML examples/Urbansounds",
    ],
)
def test_get_datasets_by_project(
    project: str,
    client: TestClient,
):

    response = client.post("/datasets/search", json={"project": project})
    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_json) == 2
    assert isinstance(response_json, list)
    for dataset in response_json:
        assert dataset["project"] == project


@pytest.mark.parametrize("dataset_id", ["e-f581e44aa3ee42f68206f3ec5d4b1ebc"])
def test_get_dataset_by_id(dataset_id: str, client: TestClient):
    response = client.get(f"/datasets/{dataset_id}")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()

    for key in ("id", "name", "project", "tags", "files"):
        assert key in response_json


@pytest.mark.parametrize("file_path", ["./test_data/small_dataset.zip"])
def test_create_dataset(file_path: str, client: TestClient):
    response = client.post(
        "/datasets/",
        # files=
        data={
            "dataset_name": "dataset_42",
            "project_name": "test_create_dataset",
        },
        files={"file": open(Path(__file__).parent.joinpath(file_path), "rb")},
    )
    dataset = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    # assert dataset["name"] == "dataset_42"
    # assert dataset["project"] == "test_create_dataset"
    # Perform cleanup of data
    ClearMLDataset.get(id=dataset["id"]).delete()
