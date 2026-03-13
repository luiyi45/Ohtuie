from pydantic import BaseModel
from typing import List, Dict, Any

class AdminStatistics(BaseModel):
    total_users: int
    active_users: int
    total_cycles: int
    avg_cycle_duration: float
    avg_period_duration: float
    failed_logins_24h: int
    failed_logins_last_7_days: Dict[str, int] = {} # e.g., {"2026-02-12": 5, ...}
    flow_analysis: Dict[str, int] # e.g., {"light": 10, "medium": 15, "heavy": 5}
    user_registrations_last_7_days: Dict[str, int] # e.g., {"2026-02-12": 5, ...}
    age_distribution: Dict[str, int] # e.g., {"<18": 10, "18-25": 20, ...}
