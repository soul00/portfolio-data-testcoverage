"""HTTP API around the validation engine."""

from contextlib import asynccontextmanager
from dataclasses import asdict
from datetime import datetime
from typing import Annotated

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from quality_gate.gate import GateConfig, run_gate
from quality_gate.storage import SessionLocal, ValidationRun, create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(title="quality-gate", version="0.1.0", lifespan=lifespan)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Record = dict[str, str | int | float | bool | None]


class GateConfigIn(BaseModel):
    model_config = ConfigDict(strict=True)

    expected_schema: dict[str, str]
    min_rows: int = 1
    max_null_fraction: float = Field(default=0.0, ge=0.0, le=1.0)
    max_duplicate_fraction: float = Field(default=0.0, ge=0.0, le=1.0)
    label_column: str | None = None
    min_class_fraction: float = Field(default=0.0, ge=0.0, le=1.0)


class ValidateRequest(BaseModel):
    records: list[Record]
    config: GateConfigIn


class CheckOut(BaseModel):
    name: str
    passed: bool
    details: dict


class ValidateResponse(BaseModel):
    passed: bool
    checks: list[CheckOut]


class RunRequest(BaseModel):
    dataset: str = Field(min_length=1, max_length=200, pattern=r"^[A-Za-z0-9._-]+$")
    records: list[Record]
    config: GateConfigIn


class RunResponse(BaseModel):
    id: int
    dataset: str
    created_at: datetime
    passed: bool
    checks: list[CheckOut]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/validate", responses={400: {"description": "Malformed request body"}})
def validate(request: ValidateRequest) -> ValidateResponse:
    df = pd.DataFrame(request.records)
    result = run_gate(df, GateConfig(**request.config.model_dump()))
    return ValidateResponse(
        passed=result.passed,
        checks=[CheckOut(name=c.name, passed=c.passed, details=c.details) for c in result.checks],
    )


@app.post("/runs", status_code=201, responses={400: {"description": "Malformed request body"}})
def create_run(request: RunRequest, db: Session = Depends(get_db)) -> RunResponse:
    df = pd.DataFrame(request.records)
    result = run_gate(df, GateConfig(**request.config.model_dump()))
    run = ValidationRun(
        dataset=request.dataset,
        passed=result.passed,
        checks=[asdict(check) for check in result.checks],
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return RunResponse(**_run_as_dict(run))


@app.get("/runs")
def list_runs(
    limit: Annotated[int, Query(ge=1, le=100)] = 20, db: Session = Depends(get_db)
) -> list[RunResponse]:
    runs = db.scalars(select(ValidationRun).order_by(ValidationRun.id.desc()).limit(limit))
    return [RunResponse(**_run_as_dict(run)) for run in runs]


@app.get("/runs/{run_id}", responses={404: {"description": "Run not found"}})
def get_run(
    run_id: Annotated[int, Path(ge=1, le=2_147_483_647)], db: Session = Depends(get_db)
) -> RunResponse:
    run = db.get(ValidationRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return RunResponse(**_run_as_dict(run))


def _run_as_dict(run: ValidationRun) -> dict:
    return {
        "id": run.id,
        "dataset": run.dataset,
        "created_at": run.created_at,
        "passed": run.passed,
        "checks": run.checks,
    }
