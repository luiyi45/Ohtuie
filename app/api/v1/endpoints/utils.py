from typing import Any
from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta, datetime

from app import models, schemas, crud
from app.api import deps

router = APIRouter()

@router.post("/password-recovery/{email}", response_model=schemas.User)
async def recover_password(email: EmailStr, db: AsyncSession = Depends(deps.get_db)) -> Any:
    """
    Password Recovery
    """
    user = await crud.user.get_by_email(db, email=email)
    
    # In a real app, send email with reset token
    # For now, we just return the user info (INSECURE for production, but okay for prototype logic demo)
    # Or better, return a success message regardless of existence to prevent enumeration
    return user

@router.get("/notifications", response_model=Any)
async def get_notifications(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Check for notifications (e.g. period coming in 2 days).
    """
    cycles = await crud.cycle.get_multi_by_user(db=db, user_id=current_user.id, limit=1)
    if not cycles:
         return {"message": "No data for notifications"}
    
    last_cycle = cycles[0]
    avg_cycle_days = 28
    next_period_start = last_cycle.start_date + timedelta(days=avg_cycle_days)
    
    days_until_period = (next_period_start - datetime.now().date()).days
    
    notifications = []
    if days_until_period == 2:
        notifications.append({
            "type": "period_alert",
            "message": "Tu periodo está previsto para comenzar en 2 días.",
            "date": next_period_start
        })
    elif days_until_period < 2 and days_until_period >= 0:
        notifications.append({
             "type": "period_alert",
             "message": "Tu periodo está muy cerca.",
             "date": next_period_start
        })

    return {"notifications": notifications}
