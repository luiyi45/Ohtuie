from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.db.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String, nullable=False) # e.g., "failed_login", "user_registration", "system_update"
    description = Column(String, nullable=True)
    metadata_json = Column(JSONB, nullable=True) # Extra data like IP, user agent, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
