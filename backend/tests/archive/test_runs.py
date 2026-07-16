import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from quality_gate.api import app
from quality_gate.storage import SessionLocal, ValidationRun


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        with SessionLocal() as db:
            db.execute(delete(ValidationRun))
            db.commit()
        yield test_client


def run_payload(dataset: str = "imdb-train") -> dict:
    return {
        "dataset": dataset,
        "records": [
            {"text": "good movie", "label": 1},
            {"text": "bad movie", "label": 0},
        ],
        "config": {"expected_schema": {"text": "str", "label": "int64"}},
    }


class TestCreateRun:
    def test_returns_stored_run(self, client):
        response = client.post("/runs", json=run_payload())
        assert response.status_code == 201
        body = response.json()
        assert body["dataset"] == "imdb-train"
        assert body["passed"] is True
        assert body["id"] > 0
        assert body["created_at"] is not None

    def test_failing_gate_is_stored_too(self, client):
        payload = run_payload()
        payload["records"] = []
        body = client.post("/runs", json=payload).json()
        assert body["passed"] is False


class TestGetRun:
    def test_unknown_id_returns_404(self, client):
        response = client.get("/runs/999999")
        assert response.status_code == 404


class TestListRuns:
    def test_newest_first(self, client):
        first = client.post("/runs", json=run_payload("dataset-a")).json()
        second = client.post("/runs", json=run_payload("dataset-b")).json()
        runs = client.get("/runs").json()
        assert [run["id"] for run in runs] == [second["id"], first["id"]]

    def test_limit(self, client):
        for name in ("a", "b", "c"):
            client.post("/runs", json=run_payload(name))
        runs = client.get("/runs", params={"limit": 2}).json()
        assert len(runs) == 2
