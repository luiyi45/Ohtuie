import json
import os
from collections import Counter
from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/moods/library", response_model=Dict[str, Any])
async def get_mood_library(
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get the library of moods with messages, advice, and tips.
    """
    library_path = os.path.join("app", "resources", "mood_library.json")
    if not os.path.exists(library_path):
        raise HTTPException(status_code=404, detail="Mood library not found")
    
    with open(library_path, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/stats/moods", response_model=Dict[str, Any])
async def get_mood_stats(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get mood frequency statistics for a date range.
    """
    logs = await crud.daily_log.get_multi_by_user_and_date_range(
        db=db, user_id=current_user.id, start_date=start_date, end_date=end_date
    )
    
    all_moods = []
    daily_stats = []
    
    for log in logs:
        if log.moods:
            all_moods.extend(log.moods)
        
        # Determine intensity (0 to 1) based on number of moods or specialized logic
        # For now, let's say intensity is based on presence of moods
        intensity = 0.5 if log.moods else 0.0
        if len(log.moods) > 2: intensity = 0.8
        
        daily_stats.append({
            "date": log.date,
            "moods": log.moods,
            "intensity": intensity
        })

    # Find predominant mood
    predominant = "normal"
    if all_moods:
        count = Counter(all_moods)
        predominant = count.most_common(1)[0][0]

    return {
        "predominant": predominant,
        "frequencies": dict(Counter(all_moods)),
        "daily": daily_stats,
        "count": len(logs)
    }

@router.get("", response_model=List[schemas.DailyLog])
# ... rest same ...
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
