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


class TestRuns:
    def test_created_run_can_be_fetched(self, client):
        created = client.post("/runs", json=run_payload())
        assert created.status_code == 201
        fetched = client.get(f"/runs/{created.json()['id']}").json()
        assert fetched == created.json()
