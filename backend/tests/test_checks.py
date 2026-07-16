import pandas as pd

from quality_gate.checks import (
    check_duplicates,
    check_label_balance,
    check_null_rates,
    check_row_count,
    check_schema,
)


class TestRowCount:
    def test_passes_above_minimum(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        assert check_row_count(df, min_rows=2).passed

    def test_fails_below_minimum(self):
        df = pd.DataFrame({"a": [1, 2]})
        result = check_row_count(df, min_rows=3)
        assert not result.passed
        assert result.details == {"rows": 2, "min_rows": 3}


class TestSchema:
    def test_passes_on_exact_match(self):
        df = pd.DataFrame({"text": ["a"], "label": [0]})
        assert check_schema(df, {"text": "str", "label": "int64"}).passed

    def test_fails_on_dtype_mismatch(self):
        df = pd.DataFrame({"label": [1.5]})
        result = check_schema(df, {"label": "int64"})
        assert not result.passed
        assert result.details["mismatched"] == {"label": {"expected": "int64", "actual": "float64"}}


class TestNullRates:
    def test_passes_with_no_nulls(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        assert check_null_rates(df, max_fraction=0.0).passed

    def test_fails_above_threshold(self):
        df = pd.DataFrame({"a": [1, None, None, None]})
        result = check_null_rates(df, max_fraction=0.5)
        assert not result.passed
        assert result.details["offending"] == {"a": 0.75}


class TestDuplicates:
    def test_passes_with_unique_rows(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        assert check_duplicates(df, max_fraction=0.0).passed

    def test_fails_above_threshold(self):
        df = pd.DataFrame({"a": [1, 1, 1, 2]})
        result = check_duplicates(df, max_fraction=0.25)
        assert not result.passed
        assert result.details["fraction"] == 0.5


class TestLabelBalance:
    def test_passes_when_balanced(self):
        df = pd.DataFrame({"label": [0, 0, 1, 1]})
        assert check_label_balance(df, "label", min_class_fraction=0.4).passed

    def test_fails_when_class_below_minimum(self):
        df = pd.DataFrame({"label": [0, 0, 0, 1]})
        result = check_label_balance(df, "label", min_class_fraction=0.4)
        assert not result.passed
        assert result.details["offending"] == {"1": 0.25}
