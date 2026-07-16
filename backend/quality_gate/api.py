"""HTTP API around the validation engine."""

import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

from quality_gate.gate import GateConfig, run_gate

app = FastAPI(title="quality-gate", version="0.1.0")


class GateConfigIn(BaseModel):
    expected_schema: dict[str, str]
    min_rows: int = 1
    max_null_fraction: float = Field(default=0.0, ge=0.0, le=1.0)
    max_duplicate_fraction: float = Field(default=0.0, ge=0.0, le=1.0)
    label_column: str | None = None
    min_class_fraction: float = Field(default=0.0, ge=0.0, le=1.0)


class ValidateRequest(BaseModel):
    records: list[dict]
    config: GateConfigIn


class CheckOut(BaseModel):
    name: str
    passed: bool
    details: dict


class ValidateResponse(BaseModel):
    passed: bool
    checks: list[CheckOut]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/validate")
def validate(request: ValidateRequest) -> ValidateResponse:
    df = pd.DataFrame(request.records)
    result = run_gate(df, GateConfig(**request.config.model_dump()))
    return ValidateResponse(
        passed=result.passed,
        checks=[CheckOut(name=c.name, passed=c.passed, details=c.details) for c in result.checks],
    )
