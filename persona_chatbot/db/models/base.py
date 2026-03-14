from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    """Shared declarative base for SQLAlchemy models."""
