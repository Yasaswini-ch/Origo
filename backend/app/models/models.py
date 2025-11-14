"""Database models for the generic-saas-app backend."""

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./items.db"

# Create the SQLite engine and session factory used across the app.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Item(Base):
    """SQLAlchemy model representing an item stored in the database."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
