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


class TestHealth:
    def test_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestValidate:
    def test_response_lists_every_check(self):
        payload = {"records": clean_records(), "config": imdb_like_config()}
        names = [check["name"] for check in client.post("/validate", json=payload).json()["checks"]]
        assert names == ["row_count", "schema", "null_rates", "duplicates", "label_balance"]

    def test_empty_records_fail_the_gate(self):
        payload = {"records": [], "config": imdb_like_config()}
        response = client.post("/validate", json=payload)
        assert response.status_code == 200
        assert response.json()["passed"] is False

    def test_missing_config_is_rejected(self):
        response = client.post("/validate", json={"records": clean_records()})
        assert response.status_code == 422

    def test_threshold_out_of_range_is_rejected(self):
        payload = {
            "records": clean_records(),
            "config": imdb_like_config(max_null_fraction=1.5),
        }
        response = client.post("/validate", json=payload)
        assert response.status_code == 422

    def test_label_column_optional(self):
        payload = {
            "records": clean_records(),
            "config": imdb_like_config(label_column=None),
        }
        body = client.post("/validate", json=payload).json()
        assert body["passed"] is True
        assert "label_balance" not in [check["name"] for check in body["checks"]]
