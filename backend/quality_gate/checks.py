"""Individual validation checks. Each one inspects a DataFrame and returns a CheckResult."""

from dataclasses import dataclass

import pandas as pd


@dataclass
class CheckResult:
    name: str
    passed: bool
    details: dict


def check_row_count(df: pd.DataFrame, min_rows: int) -> CheckResult:
    return CheckResult(
        name="row_count",
        passed=len(df) >= min_rows,
        details={"rows": len(df), "min_rows": min_rows},
    )


def check_schema(df: pd.DataFrame, expected: dict[str, str]) -> CheckResult:
    actual = {column: str(dtype) for column, dtype in df.dtypes.items()}
    missing = sorted(set(expected) - set(actual))
    unexpected = sorted(set(actual) - set(expected))
    mismatched = {
        column: {"expected": expected[column], "actual": actual[column]}
        for column in expected
        if column in actual and actual[column] != expected[column]
    }
    return CheckResult(
        name="schema",
        passed=not (missing or unexpected or mismatched),
        details={"missing": missing, "unexpected": unexpected, "mismatched": mismatched},
    )


def check_null_rates(df: pd.DataFrame, max_fraction: float) -> CheckResult:
    if df.empty:
        return CheckResult(name="null_rates", passed=False, details={"reason": "empty dataset"})
    rates = df.isna().mean()
    offending = {column: round(rate, 4) for column, rate in rates.items() if rate > max_fraction}
    return CheckResult(
        name="null_rates",
        passed=not offending,
        details={"max_fraction": max_fraction, "offending": offending},
    )


def check_duplicates(df: pd.DataFrame, max_fraction: float) -> CheckResult:
    if df.empty:
        return CheckResult(name="duplicates", passed=False, details={"reason": "empty dataset"})
    fraction = float(df.duplicated().mean())
    return CheckResult(
        name="duplicates",
        passed=fraction <= max_fraction,
        details={"fraction": round(fraction, 4), "max_fraction": max_fraction},
    )


def check_label_balance(df: pd.DataFrame, column: str, min_class_fraction: float) -> CheckResult:
    if column not in df.columns:
        return CheckResult(
            name="label_balance",
            passed=False,
            details={"reason": f"column '{column}' not found"},
        )
    if df.empty:
        return CheckResult(name="label_balance", passed=False, details={"reason": "empty dataset"})
    fractions = df[column].value_counts(normalize=True)
    offending = {
        str(label): round(fraction, 4)
        for label, fraction in fractions.items()
        if fraction < min_class_fraction
    }
    return CheckResult(
        name="label_balance",
        passed=not offending,
        details={"min_class_fraction": min_class_fraction, "offending": offending},
    )
