from pathlib import Path

import pytest
from fastapi import status
from fastapi.testclient import TestClient


def test_get_all_datasets(
    client: TestClient,
):
    response = client.post("/datasets/search", json={})
    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response_json, list)
    # since is demo server, possible that someone added extra
    # but at minimum, clearml has 2 example datasets
    assert len(response_json) >= 2


@pytest.mark.parametrize(
    "project",
    [
        "ClearML - Nvidia Framework Examples/TLTv3",
        "ClearML - Nvidia Framework Examples/Clara",
    ],
)
def test_get_datasets_by_project(
    project: str,
    client: TestClient,
):

    response = client.post("/datasets/search", json={"project": project})
    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_json) == 1  # both projects should have only 1 dataset
    assert isinstance(response_json, list)
    for dataset in response_json:
        assert dataset["project"] == project


@pytest.mark.parametrize("dataset_id", ["9751c847f6664f52a096e1264b258fad"])
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
    print(response.json())
    assert response.status_code == status.HTTP_201_CREATED
