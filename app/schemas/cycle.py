from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date, datetime

class CycleBase(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    notes: Optional[str] = None

class CycleCreate(CycleBase):
    pass

class CycleUpdate(CycleBase):
    pass

class CycleInDBBase(CycleBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Cycle(CycleInDBBase):
    pass
