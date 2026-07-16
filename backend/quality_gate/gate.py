"""Gate decision: run the configured checks against a dataset version."""

from dataclasses import dataclass, field

import pandas as pd

from quality_gate.checks import (
    CheckResult,
    check_duplicates,
    check_label_balance,
    check_null_rates,
    check_row_count,
    check_schema,
)


@dataclass
class GateConfig:
    expected_schema: dict[str, str]
    min_rows: int = 1
    max_null_fraction: float = 0.0
    max_duplicate_fraction: float = 0.0
    label_column: str | None = None
    min_class_fraction: float = 0.0


@dataclass
class GateResult:
    passed: bool
    checks: list[CheckResult] = field(default_factory=list)

    def failed_checks(self) -> list[CheckResult]:
        return [check for check in self.checks if not check.passed]


def run_gate(df: pd.DataFrame, config: GateConfig) -> GateResult:
    checks = [
        check_row_count(df, config.min_rows),
        check_schema(df, config.expected_schema),
        check_null_rates(df, config.max_null_fraction),
        check_duplicates(df, config.max_duplicate_fraction),
    ]
    if config.label_column is not None:
        checks.append(check_label_balance(df, config.label_column, config.min_class_fraction))
    return GateResult(passed=all(check.passed for check in checks), checks=checks)
