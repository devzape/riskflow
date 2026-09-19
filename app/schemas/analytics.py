from pydantic import BaseModel
from typing import List, Dict


class DailyVolume(BaseModel):
    date: str
    total_amount: float
    transaction_count: int


class TopAccount(BaseModel):
    account_id: int
    alert_count: int


class AnalyticsSummary(BaseModel):
    total_transactions: int
    total_amount: float
    flagged_transactions: int
    flagged_rate: float
    daily_volume: List[DailyVolume]
    top_flagged_accounts: List[TopAccount]
    alerts_by_severity: Dict[str, int]