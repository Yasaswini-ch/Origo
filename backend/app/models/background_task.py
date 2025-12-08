"""BackgroundTaskStatus model definition."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database import Base


class BackgroundTaskStatus(Base):
    __tablename__ = "background_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    detail = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
