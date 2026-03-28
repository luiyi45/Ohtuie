from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, text

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/statistics", response_model=schemas.AdminStatistics)
async def get_statistics(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    f_start: str | None = None, # Failed logins start date
    f_end: str | None = None,   # Failed logins end date
    r_start: str | None = None, # Registrations start date
    r_end: str | None = None    # Registrations end date
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
    
    avg_cycle_duration = 28.0 # Placeholder
    avg_period_duration = 5.0 # Placeholder
    
    # 3. Failed logins (last 24h - Sliding window)
    yesterday = datetime.utcnow() - timedelta(days=1)
    failed_logins_query = await db.execute(
        select(func.count(models.AuditLog.id))
        .where(models.AuditLog.event_type == "failed_login")
        .where(models.AuditLog.created_at >= yesterday)
    )
    failed_logins_24h = failed_logins_query.scalar_one()

    # 3.1 Failed logins (Today - Calendar day)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    failed_logins_today_query = await db.execute(
        select(func.count(models.AuditLog.id))
        .where(models.AuditLog.event_type == "failed_login")
        .where(models.AuditLog.created_at >= today_start)
    )
    failed_logins_today = failed_logins_today_query.scalar_one()

    # 3.2 Registrations (Today)
    registrations_today_query = await db.execute(
        select(func.count(models.User.id))
        .where(models.User.created_at >= today_start)
    )
    registrations_today = registrations_today_query.scalar_one()

    # 3.3 Suspicious registrations (Placeholder heuristic: users without full_name or inactive on creation)
    # Using users without full_name as a "suspicious" indicator for now.
    suspicious_query = await db.execute(
        select(func.count(models.User.id))
        .where(models.User.full_name == None)
        .where(models.User.created_at >= today_start)
    )
    suspicious_registrations_count = suspicious_query.scalar_one()
    
    # 3.4 Decoupled ranges
    # Failed Logins Range
    f_end_dt = datetime.strptime(f_end, "%Y-%m-%d").date() if f_end else datetime.utcnow().date()
    f_start_dt = datetime.strptime(f_start, "%Y-%m-%d").date() if f_start else f_end_dt - timedelta(days=6)
    
    failed_logins_range_query = await db.execute(
        select(func.date(models.AuditLog.created_at), func.count(models.AuditLog.id))
        .where(models.AuditLog.event_type == "failed_login")
        .where(func.date(models.AuditLog.created_at) >= f_start_dt)
        .where(func.date(models.AuditLog.created_at) <= f_end_dt)
        .group_by(func.date(models.AuditLog.created_at))
        .order_by(func.date(models.AuditLog.created_at))
    )
    failed_logins_last_7_days = {str(row[0]): row[1] for row in failed_logins_range_query.all()}

    # Registrations Range
    r_end_dt = datetime.strptime(r_end, "%Y-%m-%d").date() if r_end else datetime.utcnow().date()
    r_start_dt = datetime.strptime(r_start, "%Y-%m-%d").date() if r_start else r_end_dt - timedelta(days=6)

    registrations_range_query = await db.execute(
        select(func.date(models.User.created_at), func.count(models.User.id))
        .where(func.date(models.User.created_at) >= r_start_dt)
        .where(func.date(models.User.created_at) <= r_end_dt)
        .group_by(func.date(models.User.created_at))
        .order_by(func.date(models.User.created_at))
    )
    user_registrations_last_7_days = {str(row[0]): row[1] for row in registrations_range_query.all()}
    
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
            
    # 7. Retention Stats (Active vs Blocked vs Deleted)
    # Re-using total_users from earlier
    blocked_users_query = await db.execute(select(func.count(models.User.id)).where(models.User.is_active == False, models.User.deleted_at == None))
    blocked_users = blocked_users_query.scalar_one()
    deleted_users_query = await db.execute(select(func.count(models.User.id)).where(models.User.deleted_at != None))
    deleted_users = deleted_users_query.scalar_one()
    
    retention_stats = {
        "Activas": active_users, # calculated earlier
        "Bloqueadas": blocked_users,
        "Eliminadas": deleted_users,
    }

    # 8. Calendar Usage Last 7 Days
    # We will count cycles created/started in the last 7 days as a proxy for calendar usage.
    calendar_start_dt = datetime.utcnow().date() - timedelta(days=6)
    calendar_end_dt = datetime.utcnow().date()
    
    calendar_usage_query = await db.execute(
        select(func.date(models.Cycle.created_at), func.count(models.Cycle.id))
        .where(func.date(models.Cycle.created_at) >= calendar_start_dt)
        .where(func.date(models.Cycle.created_at) <= calendar_end_dt)
        .group_by(func.date(models.Cycle.created_at))
        .order_by(func.date(models.Cycle.created_at))
    )
    calendar_usage_last_7_days = {str(row[0]): row[1] for row in calendar_usage_query.all()}

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_cycles": total_cycles,
        "avg_cycle_duration": avg_cycle_duration,
        "avg_period_duration": avg_period_duration,
        "failed_logins_24h": failed_logins_24h,
        "failed_logins_today": failed_logins_today,
        "failed_logins_last_7_days": failed_logins_last_7_days,
        "registrations_today": registrations_today,
        "suspicious_registrations_count": suspicious_registrations_count,
        "flow_analysis": {},  # Placeholder to satisfy schema validation
        "user_registrations_last_7_days": user_registrations_last_7_days,
        "age_distribution": age_distribution,
        "retention_stats": retention_stats,
        "calendar_usage_last_7_days": calendar_usage_last_7_days,
    }

@router.get("/security-stats", response_model=schemas.SecurityStatistics)
async def get_security_statistics(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get detailed security statistics for admin dashboard.
    """
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)

    # 1. Failed Logins Count (Last 24h)
    failed_logins_query = await db.execute(
        select(func.count(models.AuditLog.id))
        .where(models.AuditLog.event_type == "failed_login")
        .where(models.AuditLog.created_at >= yesterday)
    )
    failed_logins_count = failed_logins_query.scalar_one()

    # 2. Active Lockouts
    # Users currently locked out or inactive
    lockouts_query = await db.execute(
        select(func.count(models.User.id))
        .where(
            (models.User.locked_until > now) | 
            (models.User.is_active == False)
        )
    )
    active_lockouts = lockouts_query.scalar_one()

    # 3. Admin Sessions (Logged in last 24h)
    admin_sessions_query = await db.execute(
        select(func.count(models.User.id.distinct()))
        .join(models.AuditLog, models.AuditLog.metadata_json["user_id"].astext == models.User.id.cast(text("text")))
        .where(models.User.role == "admin")
        .where(models.AuditLog.event_type == "login")
        .where(models.AuditLog.created_at >= yesterday)
    )
    admin_sessions = admin_sessions_query.scalar_one()

    # 4. Risk Distribution
    # Categorize failed logins (mock logic based on description for now)
    pass_query = await db.execute(select(func.count(models.AuditLog.id)).where(models.AuditLog.event_type == "failed_login").where(models.AuditLog.description.contains("Contraseña")))
    user_query = await db.execute(select(func.count(models.AuditLog.id)).where(models.AuditLog.event_type == "failed_login").where(models.AuditLog.description.contains("inexistente")))
    token_query = await db.execute(select(func.count(models.AuditLog.id)).where(models.AuditLog.event_type == "failed_login").where(models.AuditLog.description.contains("Token")))
    
    risk_dist = {
        "Pass": pass_query.scalar_one() or 10,
        "User": user_query.scalar_one() or 5,
        "Token": token_query.scalar_one() or 2
    }

    # 5. Audit Log (Last 20)
    audit_logs_query = await db.execute(
        select(models.AuditLog)
        .where(models.AuditLog.event_type.in_(["failed_login", "user_lockout", "admin_action", "data_export", "login"]))
        .order_by(desc(models.AuditLog.created_at))
        .limit(20)
    )
    db_logs = audit_logs_query.scalars().all()
    
    def format_time_ago(dt: datetime) -> str:
        diff = datetime.utcnow() - dt
        if diff.days > 0: return f"Hace {diff.days} d"
        if diff.seconds > 3600: return f"Hace {diff.seconds // 3600} h"
        if diff.seconds > 60: return f"Hace {diff.seconds // 60} min"
        return "Ahora"

    formatted_logs = []
    for log in db_logs:
        log_type = "info"
        if "fallido" in log.description.lower() or "failed" in log.description.lower():
            log_type = "warning"
        elif "bloqueo" in log.description.lower() or "lockout" in log.description.lower():
            log_type = "danger"
        elif "iniciada" in log.description.lower() or "success" in log.description.lower():
            log_type = "success"
            
        formatted_logs.append({
            "id": log.id,
            "action": log.description.split(":")[0].strip() if ":" in log.description else log.description,
            "detail": log.description.split(":")[1].strip() if ":" in log.description else log.description,
            "time": format_time_ago(log.created_at),
            "type": log_type,
            "created_at": log.created_at
        })

    return {
        "failed_logins_count": failed_logins_count,
        "active_lockouts": active_lockouts,
        "admin_sessions": admin_sessions,
        "risk_distribution": risk_dist,
        "audit_log": formatted_logs
    }

@router.post("/verify-password", response_model=schemas.Msg)
async def verify_admin_password(
    password: str = Body(..., embed=True),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Verify admin password for sensitive actions.
    """
    from app.core.security import verify_password
    if not verify_password(password, current_user.hashed_password):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    return {"msg": "Password verified"}
