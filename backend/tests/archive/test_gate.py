import pandas as pd

from quality_gate.gate import GateConfig, run_gate


def good_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {"text": ["good movie", "bad movie", "fine movie", "great movie"], "label": [1, 0, 0, 1]}
    )


def imdb_like_config(**overrides) -> GateConfig:
    defaults = dict(
        expected_schema={"text": "str", "label": "int64"},
        min_rows=2,
        max_null_fraction=0.0,
        max_duplicate_fraction=0.0,
        label_column="label",
        min_class_fraction=0.3,
    )
    defaults.update(overrides)
    return GateConfig(**defaults)


class TestRunGate:
    def test_runs_all_configured_checks(self):
        result = run_gate(good_dataframe(), imdb_like_config())
        names = [check.name for check in result.checks]
        assert names == ["row_count", "schema", "null_rates", "duplicates", "label_balance"]

    def test_label_check_skipped_when_not_configured(self):
        result = run_gate(good_dataframe(), imdb_like_config(label_column=None))
        names = [check.name for check in result.checks]
        assert "label_balance" not in names
        assert result.passed

    def test_multiple_failures_all_reported(self):
        df = pd.DataFrame({"text": ["same", "same"], "label": [1, 1]})
        df = pd.concat([df, df], ignore_index=True)
        result = run_gate(df, imdb_like_config())
        failed = [check.name for check in result.failed_checks()]
        assert "duplicates" in failed
        assert not result.passed

    def test_empty_dataset_fails_the_gate(self):
        result = run_gate(pd.DataFrame(), imdb_like_config())
        assert not result.passed
        failed = [check.name for check in result.failed_checks()]
        assert "row_count" in failed
