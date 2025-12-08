"""Project model definition."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    project_type = Column(String, nullable=True)
    tech_stack = Column(String, nullable=True)
    complexity = Column(Float, nullable=True)
    extra_metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    generation_attempts = relationship(
        "GenerationAttempt", back_populates="project", cascade="all, delete-orphan"
    )
    feedback = relationship(
        "UserFeedback", back_populates="project", cascade="all, delete-orphan"
    )
