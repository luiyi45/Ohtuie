from sqlalchemy import Boolean, Column, String, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    birthday = Column(DateTime(timezone=True), nullable=True)
    role = Column(String, default="user", nullable=False) # admin, user
    cycle_duration = Column(Integer, nullable=True)
    period_duration = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships with cascade delete
    cycles = relationship("Cycle", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    daily_logs = relationship("DailyLog", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
