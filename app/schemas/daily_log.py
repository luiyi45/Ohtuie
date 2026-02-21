import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID

class DailyLogBase(BaseModel):
    date: Optional[datetime.date] = None
    flow: Optional[str] = None # "none", "light", "medium", "heavy"
    symptoms: List[str] = [] # ["cramps", "bloating"]
    moods: List[str] = [] # ["happy", "irritable"]
    notes: Optional[str] = None

class DailyLogCreate(DailyLogBase):
    pass

class DailyLogUpdate(DailyLogBase):
    pass

class DailyLogInDBBase(DailyLogBase):
    id: UUID
    user_id: UUID
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)

class DailyLog(DailyLogInDBBase):
    pass
