"""UserFeedback model definition."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import relationship

from app.database import Base


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    generation_attempt_id = Column(Integer, ForeignKey("generation_attempts.id"), nullable=True)

    user_rating = Column(Integer, nullable=True)
    usefulness_score = Column(Float, nullable=True)
    accuracy_score = Column(Float, nullable=True)
    comments = Column(Text, nullable=True)

    extra_metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    project = relationship("Project", back_populates="feedback")
    generation_attempt = relationship("GenerationAttempt")
