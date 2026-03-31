from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class AdminStatistics(BaseModel):
    total_users: int
    active_users: int
    total_cycles: int
    avg_cycle_duration: float
    avg_period_duration: float
    failed_logins_24h: int
    failed_logins_today: int
    failed_logins_last_7_days: Dict[str, int] = {} # e.g., {"2026-02-12": 5, ...}
    registrations_today: int
    suspicious_registrations_count: int
    flow_analysis: Dict[str, int] = {} # Keeping this for backwards compatibility for now, but will be empty
    user_registrations_last_7_days: Dict[str, int] = {}
    age_distribution: Dict[str, int] = {}
    retention_stats: Dict[str, int] = {}
    calendar_usage_last_7_days: Dict[str, int] = {}
    failed_logins: List[Dict[str, Any]] = []
    blocked_users_count: int = 0
    logged_in_today: int = 0
    new_users_month_percentage: float = 0.0
    activity_today_percentage: float = 0.0

class SecurityAuditLogEntry(BaseModel):
    id: UUID
    action: str
    detail: str
    time: str
    type: str # warning, danger, info, success
    created_at: datetime

class SecurityStatistics(BaseModel):
    failed_logins_count: int
    active_lockouts: int
    admin_sessions: int
    risk_distribution: Dict[str, int] # e.g., {"Pass": 45, "User": 30, "Token": 25}
    audit_log: List[SecurityAuditLogEntry]

class AuditLogCreate(BaseModel):
    event_type: str
    description: str
    metadata_json: Optional[Dict[str, Any]] = None

class DataAnalysis(BaseModel):
    user_pulse: Dict[str, Any]
    engagement: Dict[str, Any]
    funnel: List[Dict[str, Any]]
    sentiment: Dict[str, Any]
    msg: Optional[str] = None
