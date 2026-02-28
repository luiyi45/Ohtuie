from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import timedelta

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Cycle])
async def read_cycles(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve cycles.
    """
    if current_user.role == "admin":
        cycles = await crud.cycle.get_multi(db, skip=skip, limit=limit) # Admin sees all? Maybe logic needs refinement
    else:
        cycles = await crud.cycle.get_multi_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)
    return cycles

@router.post("/", response_model=schemas.Cycle)
async def create_cycle(
    *,
    db: AsyncSession = Depends(deps.get_db),
    cycle_in: schemas.CycleCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new cycle.
    """
    cycle = await crud.cycle.create_with_owner(db=db, obj_in=cycle_in, user_id=current_user.id)
    return cycle

@router.put("/{id}", response_model=schemas.Cycle)
async def update_cycle(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: UUID,
    cycle_in: schemas.CycleUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a cycle.
    """
    cycle = await crud.cycle.get(db=db, id=id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    if current_user.role != "admin" and cycle.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    cycle = await crud.cycle.update(db=db, db_obj=cycle, obj_in=cycle_in)
    return cycle

@router.delete("/{id}", response_model=schemas.Cycle)
async def delete_cycle(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: UUID,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a cycle.
    """
    cycle = await crud.cycle.get(db=db, id=id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    if current_user.role != "admin" and cycle.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    cycle = await crud.cycle.remove(db=db, id=id)
    return cycle

@router.get("/prediction", response_model=Any)
async def get_prediction(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get predictions for period, ovulation, and fertile window.
    """
    # Logic for prediction
    # 1. Get all cycles to calculate average duration
    cycles = await crud.cycle.get_multi_by_user(db=db, user_id=current_user.id, limit=100)
    if not cycles:
         return {"message": "Not enough data for predictions"}
    
    # Calculate average cycle duration if we have at least 2 cycles
    avg_cycle_days = current_user.cycle_duration or 28
    if len(cycles) >= 2:
        durations = []
        for i in range(len(cycles) - 1):
            # Cycles are ordered by start_date desc, so cycles[i] is newer than cycles[i+1]
            diff = (cycles[i].start_date - cycles[i+1].start_date).days
            if 15 < diff < 45: # Sanity check for cycle length
                durations.append(diff)
        
        if durations:
            avg_cycle_days = sum(durations) // len(durations)

    last_cycle = cycles[0] # Most recent cycle
    
    next_period_start = last_cycle.start_date + timedelta(days=avg_cycle_days)
    ovulation_date = next_period_start - timedelta(days=14)
    # Fertile window is usually 5 days before ovulation plus the day of ovulation
    fertile_window_start = ovulation_date - timedelta(days=5)
    fertile_window_end = ovulation_date + timedelta(days=1)
    
    return {
        "next_period_start": next_period_start,
        "ovulation_date": ovulation_date,
        "period_duration": current_user.period_duration or 5,
        "avg_cycle_duration": avg_cycle_days,
        "fertile_window": {
            "start": fertile_window_start,
            "end": fertile_window_end
        }
    }
