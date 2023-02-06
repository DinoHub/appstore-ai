from pathlib import Path
from typing import Dict, Set

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
    "query,expected_ids",
    [
        (
            dict(project="ClearML examples/Urbansounds"),
            {
                "e-f581e44aa3ee42f68206f3ec5d4b1ebc",
                "e-21b38d1c7d22414aa4c5f5c7bda30d71",
            },
        ),
        (
            dict(id=["e-f581e44aa3ee42f68206f3ec5d4b1ebc"]),
            {"e-f581e44aa3ee42f68206f3ec5d4b1ebc"},
        ),
        (
            dict(name="UrbanSounds"),
            {
                "e-f581e44aa3ee42f68206f3ec5d4b1ebc",
                "e-21b38d1c7d22414aa4c5f5c7bda30d71",
            },
        ),
        (
            dict(tags=["preprocessed"]),
            {
                "e-f581e44aa3ee42f68206f3ec5d4b1ebc",
            },
        ),
        (dict(name="invalid"), {}),
    ],
)
def test_search_datasets(
    query: Dict, expected_ids: Set[str], client: TestClient
):
    response = client.post(
        "/datasets/search", json=query, params={"connector": "clearml"}
    )
    assert response.status_code == status.HTTP_200_OK

    results = response.json()
    assert len(results) == len(expected_ids)
    assert isinstance(results, list)

    for dataset in results:
        assert dataset["id"] in expected_ids


@pytest.mark.parametrize("dataset_id", ["e-f581e44aa3ee42f68206f3ec5d4b1ebc"])
def test_get_dataset_by_id(dataset_id: str, client: TestClient):
    response = client.get(
        f"/datasets/{dataset_id}", params={"connector": "clearml"}
    )
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()

    for key in ("id", "name", "project", "tags", "files", "artifacts"):
        assert key in response_json


def test_get_non_existent_dataset(client: TestClient):
    response = client.get(
        "/datasets/invalid_dataset", params={"connector": "clearml"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("file_path", ["./test_data/small_dataset.zip"])
def test_create_dataset(file_path: str, client: TestClient):
    response = client.post(
        "/datasets/",
        # files=
        data={
            "dataset_name": "dataset_42",
            "project_name": "test_create_dataset",
            "connector": "clearml",
        },
        files={"file": open(Path(__file__).parent.joinpath(file_path), "rb")},
    )
    dataset = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    # assert dataset["name"] == "dataset_42"
    # assert dataset["project"] == "test_create_dataset"
    # Perform cleanup of data
    ClearMLDataset.get(id=dataset["id"]).delete()


@pytest.mark.xfail(reason="Invalid file type")
def test_create_dataset_invalid_filetype():
    test_create_dataset("./test_data/invalid_dataset_type.bin")


@pytest.mark.xfail(reason="Too large dataset")
def test_create_dataset_filelimit():
    test_create_dataset("./test_data/large_dataset.zip")
