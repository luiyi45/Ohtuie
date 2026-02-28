from sqlalchemy import Column, Date, ForeignKey, Text, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base

class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, default=func.current_date())
    flow = Column(String, nullable=True) # "none", "light", "medium", "heavy"
    symptoms = Column(JSONB, nullable=True) # ["cramps", "bloating"]
    moods = Column(JSONB, nullable=True) # ["happy", "irritable"]
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="daily_logs")
