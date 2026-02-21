from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime, date

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    full_name: Optional[str] = None
    birthday: Optional[date] = None
    cycle_duration: Optional[int] = 28
    period_duration: Optional[int] = 5

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str
    role: str = "user"
    cycle_duration: int = 28
    period_duration: int = 5

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: Optional[UUID] = None
    role: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Additional properties to return via API
class User(UserInDBBase):
    pass

# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str

class UserRegistration(BaseModel):
    user: UserCreate
    cycle_start_date: Optional[date] = None
    cycle_duration: Optional[int] = 28
    period_duration: Optional[int] = 5
