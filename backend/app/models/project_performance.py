"""ProjectPerformance model definition for persisted metrics."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class ProjectPerformance(Base):
    __tablename__ = "project_performances"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    generation_attempt_id = Column(Integer, ForeignKey("generation_attempts.id"), nullable=True)

    metrics = Column(JSON, nullable=False)
    quality_score = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    project = relationship("Project")
    generation_attempt = relationship("GenerationAttempt")
