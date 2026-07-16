from pathlib import Path

import pandas as pd
import pytest

from quality_gate.checks import (
    check_duplicates,
    check_label_balance,
    check_null_rates,
    check_row_count,
    check_schema,
)

SNAPSHOT = Path(__file__).resolve().parents[1] / "data" / "imdb.parquet"

pytestmark = pytest.mark.skipif(not SNAPSHOT.exists(), reason="no dataset snapshot")


@pytest.fixture(scope="module")
def imdb():
    return pd.read_parquet(SNAPSHOT)


class TestImdbSnapshot:
    def test_row_count(self, imdb):
        result = check_row_count(imdb, min_rows=25000)
        assert result.passed, result.details

    def test_schema(self, imdb):
        result = check_schema(imdb, {"text": "str", "label": "int64"})
        assert result.passed, result.details

    def test_null_rates(self, imdb):
        result = check_null_rates(imdb, max_fraction=0.0)
        assert result.passed, result.details

    def test_duplicates(self, imdb):
        result = check_duplicates(imdb, max_fraction=0.005)
        assert result.passed, result.details

    def test_label_balance(self, imdb):
        result = check_label_balance(imdb, "label", min_class_fraction=0.45)
        assert result.passed, result.details
