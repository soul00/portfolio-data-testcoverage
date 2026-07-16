"""Database setup and models for stored validation runs."""

import os
from datetime import datetime

from sqlalchemy import JSON, DateTime, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg://gate:gate@localhost:5432/gate")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class ValidationRun(Base):
    __tablename__ = "validation_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    passed: Mapped[bool]
    checks: Mapped[list] = mapped_column(JSON)


def create_tables() -> None:
    Base.metadata.create_all(engine)
