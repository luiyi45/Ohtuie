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
    from datetime import timedelta

    logs = await crud.daily_log.get_multi_by_user_and_date_range(
        db=db, user_id=current_user.id, start_date=start_date, end_date=end_date
    )
    
    # Map existing logs by date for easy access
    logs_by_date = {log.date: log for log in logs}
    
    all_moods = []
    daily_stats = []
    
    # Step 1: Sum total moods in the range
    total_moods_in_range = 0
    current_date = start_date
    
    # We'll store counts to compute intensity in a second pass
    counts = {}
    while current_date <= end_date:
        log = logs_by_date.get(current_date)
        mood_list = log.moods if log and log.moods else []
        counts[current_date] = len(mood_list)
        total_moods_in_range += len(mood_list)
        
        if mood_list:
            all_moods.extend(mood_list)
        
        current_date += timedelta(days=1)

    # Step 2: Build the daily stats with relative intensity
    current_date = start_date
    while current_date <= end_date:
        log = logs_by_date.get(current_date)
        day_count = counts.get(current_date, 0)
        
        # Calculate intensity relative to total activity in this period
        # If total activity is 0, intensity is 0. 
        # If only 1 mood was logged all week, that day gets 1.0 (100%).
        intensity = 0.0
        if total_moods_in_range > 0:
            intensity = day_count / total_moods_in_range
            
        daily_stats.append({
            "date": current_date,
            "moods": log.moods if log else [],
            "intensity": intensity
        })
        current_date += timedelta(days=1)

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
