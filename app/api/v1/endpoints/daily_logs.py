from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("", response_model=List[schemas.DailyLog])
@router.get("/", response_model=List[schemas.DailyLog], include_in_schema=False)
async def read_daily_logs(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve daily logs for current user.
    """
    logs = await crud.daily_log.get_multi_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return logs

@router.post("", response_model=schemas.DailyLog)
@router.post("/", response_model=schemas.DailyLog, include_in_schema=False)
async def create_or_update_daily_log(
    *,
    db: AsyncSession = Depends(deps.get_db),
    log_in: schemas.DailyLogCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Create or update a daily log for a specific date (defaults to today).
    """
    target_date = log_in.date or date.today()
    
    # Check if log already exists for this date
    existing_log = await crud.daily_log.get_by_user_and_date(
        db=db, user_id=current_user.id, date=target_date
    )
    
    if existing_log:
        # Update existing log
        update_data = log_in.model_dump(exclude_unset=True)
        return await crud.daily_log.update(
            db=db, db_obj=existing_log, obj_in=update_data
        )
    
    # Create new log
    return await crud.daily_log.create_with_owner(
        db=db, obj_in=log_in, user_id=current_user.id
    )

@router.get("/{target_date}", response_model=schemas.DailyLog)
async def read_daily_log_by_date(
    target_date: date,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get daily log for a specific date.
    """
    log = await crud.daily_log.get_by_user_and_date(
        db=db, user_id=current_user.id, date=target_date
    )
    if not log:
        raise HTTPException(status_code=404, detail="Daily log not found for this date")
    return log
