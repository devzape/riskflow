from pydantic import BaseModel
from datetime import datetime

class AlertOut(BaseModel):
    id: int
    transaction_id: int
    rule_id: int
    severity: str
    created_at: datetime
    resolved: bool

    class Config:
        from_attributes = True