"""ModelPerformance model definition."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.database import Base


class ModelPerformance(Base):
    __tablename__ = "model_performances"

    id = Column(Integer, primary_key=True, index=True)
    generation_attempt_id = Column(Integer, ForeignKey("generation_attempts.id"), nullable=False)

    model_name = Column(String, nullable=False)
    generation_time_ms = Column(Integer, nullable=True)
    metrics = Column(JSON, nullable=True)
    code_quality_scores = Column(JSON, nullable=True)

    predicted_success_probability = Column(Float, nullable=True)
    estimated_quality_score = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    generation_attempt = relationship("GenerationAttempt", back_populates="model_performances")
