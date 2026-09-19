from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

class TransactionCreate(BaseModel):
    origin_account_id: int
    destination_account_id: int
    amount: Decimal

class TransactionOut(BaseModel):
    id: int
    origin_account_id: int
    destination_account_id: int
    amount: Decimal
    timestamp: datetime
    status: str

    class Config:
        from_attributes = True