from pydantic import BaseModel
from typing import List, Dict, Any

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
