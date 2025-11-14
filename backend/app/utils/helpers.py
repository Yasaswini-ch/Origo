"""Shared helper utilities for the backend, including DB session management."""

from typing import Generator

from sqlalchemy.orm import Session

from app.models.models import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session and ensures it is closed."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
