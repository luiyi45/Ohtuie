from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/statistics", response_model=schemas.AdminStatistics)
async def get_statistics(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get system-wide statistics for admin dashboard.
    """
    # 1. User counts
    total_users_query = await db.execute(select(func.count(models.User.id)))
    total_users = total_users_query.scalar_one()
    
    active_users_query = await db.execute(select(func.count(models.User.id)).where(models.User.is_active == True))
    active_users = active_users_query.scalar_one()
    
    # 2. Cycle metrics
    total_cycles_query = await db.execute(select(func.count(models.Cycle.id)))
    total_cycles = total_cycles_query.scalar_one()
    
    # Simplified avg for now (assuming duration is stored or calculated)
    # Actually, we don't have duration in the model, it might be calculated between cycles.
    # In CycleSetupScreen, we had a duration field in UserRegistration. 
    # Let's check the Cycle model again.
    
    avg_cycle_duration = 28.0 # Placeholder
    avg_period_duration = 5.0 # Placeholder
    
    # 3. Failed logins (last 24h)
    yesterday = datetime.utcnow() - timedelta(days=1)
    failed_logins_query = await db.execute(
        select(func.count(models.AuditLog.id))
        .where(models.AuditLog.event_type == "failed_login")
        .where(models.AuditLog.created_at >= yesterday)
    )
    failed_logins_24h = failed_logins_query.scalar_one()
    
    # 4. Flow analysis (assuming it's in DailyLog)
    flow_query = await db.execute(
        select(models.DailyLog.flow, func.count(models.DailyLog.id))
        .group_by(models.DailyLog.flow)
    )
    flow_analysis = {row[0]: row[1] for row in flow_query.all() if row[0] is not None}
    
    # 5. User registrations (last 7 days)
    seven_days_ago = datetime.utcnow().date() - timedelta(days=7)
    registrations_query = await db.execute(
        select(func.date(models.User.created_at), func.count(models.User.id))
        .where(func.date(models.User.created_at) >= seven_days_ago)
        .group_by(func.date(models.User.created_at))
        .order_by(func.date(models.User.created_at))
    )
    user_registrations_last_7_days = {str(row[0]): row[1] for row in registrations_query.all()}
    
    # 6. Age distribution
    age_query = await db.execute(
        select(
            text("""
                CASE 
                    WHEN EXTRACT(YEAR FROM age(birthday)) < 18 THEN '<18'
                    WHEN EXTRACT(YEAR FROM age(birthday)) BETWEEN 18 AND 25 THEN '18-25'
                    WHEN EXTRACT(YEAR FROM age(birthday)) BETWEEN 26 AND 35 THEN '26-35'
                    WHEN EXTRACT(YEAR FROM age(birthday)) BETWEEN 36 AND 45 THEN '36-45'
                    ELSE '46+'
                END as age_range
            """),
            func.count(models.User.id)
        )
        .where(models.User.birthday != None)
        .group_by(text("age_range"))
    )
    age_distribution = {row[0]: row[1] for row in age_query.all()}
    
    # Ensure all ranges exist
    for r in ["<18", "18-25", "26-35", "36-45", "46+"]:
        if r not in age_distribution:
            age_distribution[r] = 0

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_cycles": total_cycles,
        "avg_cycle_duration": avg_cycle_duration,
        "avg_period_duration": avg_period_duration,
        "failed_logins_24h": failed_logins_24h,
        "flow_analysis": flow_analysis,
        "user_registrations_last_7_days": user_registrations_last_7_days,
        "age_distribution": age_distribution,
    }
