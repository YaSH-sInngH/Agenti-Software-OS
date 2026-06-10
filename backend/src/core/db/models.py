from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from src.core.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")
    due_date = Column(DateTime, nullable=True)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

class IndexedFile(Base):
    __tablename__ = "indexed_files"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    file_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    indexed_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    message = Column(String, nullable=False)
    remind_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )