import pandas as pd

from quality_gate.checks import (
    check_duplicates,
    check_label_balance,
    check_null_rates,
    check_row_count,
    check_schema,
)


class TestRowCount:
    def test_passes_at_exact_minimum(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        assert check_row_count(df, min_rows=3).passed

    def test_fails_on_empty_dataframe(self):
        assert not check_row_count(pd.DataFrame(), min_rows=1).passed


class TestSchema:
    def test_fails_on_missing_column(self):
        df = pd.DataFrame({"text": ["a"]})
        result = check_schema(df, {"text": "str", "label": "int64"})
        assert not result.passed
        assert result.details["missing"] == ["label"]

    def test_fails_on_unexpected_column(self):
        df = pd.DataFrame({"text": ["a"], "extra": [1]})
        result = check_schema(df, {"text": "str"})
        assert not result.passed
        assert result.details["unexpected"] == ["extra"]

    def test_reports_all_problems_at_once(self):
        df = pd.DataFrame({"extra": [1], "label": [1.5]})
        result = check_schema(df, {"text": "str", "label": "int64"})
        assert result.details["missing"] == ["text"]
        assert result.details["unexpected"] == ["extra"]
        assert "label" in result.details["mismatched"]


class TestNullRates:
    def test_passes_at_exact_threshold(self):
        df = pd.DataFrame({"a": [1, None]})
        assert check_null_rates(df, max_fraction=0.5).passed

    def test_only_offending_columns_reported(self):
        df = pd.DataFrame({"clean": [1, 2], "dirty": [None, None]})
        result = check_null_rates(df, max_fraction=0.1)
        assert list(result.details["offending"]) == ["dirty"]

    def test_fails_on_empty_dataframe(self):
        result = check_null_rates(pd.DataFrame(), max_fraction=1.0)
        assert not result.passed
        assert result.details == {"reason": "empty dataset"}


class TestDuplicates:
    def test_passes_at_exact_threshold(self):
        df = pd.DataFrame({"a": [1, 1, 2, 3]})
        assert check_duplicates(df, max_fraction=0.25).passed

    def test_duplicate_means_full_row_match(self):
        df = pd.DataFrame({"a": [1, 1], "b": [1, 2]})
        assert check_duplicates(df, max_fraction=0.0).passed

    def test_fails_on_empty_dataframe(self):
        assert not check_duplicates(pd.DataFrame(), max_fraction=1.0).passed


class TestLabelBalance:
    def test_passes_with_single_class(self):
        df = pd.DataFrame({"label": [0, 0]})
        assert check_label_balance(df, "label", min_class_fraction=0.5).passed

    def test_fails_when_column_missing(self):
        df = pd.DataFrame({"text": ["a"]})
        result = check_label_balance(df, "label", min_class_fraction=0.1)
        assert not result.passed
        assert "not found" in result.details["reason"]

    def test_fails_on_empty_dataframe(self):
        df = pd.DataFrame({"label": []})
        assert not check_label_balance(df, "label", min_class_fraction=0.1).passed
