"""GenerationAttempt model definition."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class GenerationAttempt(Base):
    __tablename__ = "generation_attempts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    model_used = Column(String, nullable=False)
    success = Column(Boolean, default=False, nullable=False)
    generation_time_ms = Column(Integer, nullable=True)

    prompt = Column(Text, nullable=False)
    code_snapshot = Column(Text, nullable=True)

    code_quality_scores = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)

    error_message = Column(Text, nullable=True)

    project_type = Column(String, nullable=True)
    complexity_indicators = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    project = relationship("Project", back_populates="generation_attempts")
    model_performances = relationship(
        "ModelPerformance", back_populates="generation_attempt", cascade="all, delete-orphan"
    )
