from fastapi.testclient import TestClient

from quality_gate.api import app

client = TestClient(app)


def imdb_like_config(**overrides) -> dict:
    config = {
        "expected_schema": {"text": "str", "label": "int64"},
        "min_rows": 2,
        "label_column": "label",
        "min_class_fraction": 0.3,
    }
    config.update(overrides)
    return config


def clean_records() -> list[dict]:
    return [
        {"text": "good movie", "label": 1},
        {"text": "bad movie", "label": 0},
        {"text": "fine movie", "label": 0},
        {"text": "great movie", "label": 1},
    ]


class TestValidate:
    def test_clean_data_passes_the_gate(self):
        payload = {"records": clean_records(), "config": imdb_like_config()}
        response = client.post("/validate", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["passed"] is True
        assert all(check["passed"] for check in body["checks"])

    def test_dirty_data_fails_with_details(self):
        records = clean_records()
        records[0]["text"] = None
        payload = {"records": records, "config": imdb_like_config()}
        body = client.post("/validate", json=payload).json()
        assert body["passed"] is False
        failed = [check for check in body["checks"] if not check["passed"]]
        assert failed[0]["name"] == "null_rates"
        assert failed[0]["details"]["offending"] == {"text": 0.25}
