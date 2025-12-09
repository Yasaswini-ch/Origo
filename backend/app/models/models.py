"""Database models for the generic-saas-app backend.

This module now only defines the legacy Item model, which uses the shared
SQLAlchemy Base from ``app.database``.
"""

from sqlalchemy import Column, Integer, String

from app.database import Base


class Item(Base):
    """SQLAlchemy model representing an item stored in the database."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
