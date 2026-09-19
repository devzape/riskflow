from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

class AccountCreate(BaseModel):
    initial_balance: Decimal = Decimal("0.00")

class AccountOut(BaseModel):
    id: int
    user_id: int
    balance: Decimal
    created_at: datetime

    class Config:
        from_attributes = True