from pydantic import BaseModel, field_validator
from decimal import Decimal
from datetime import datetime

class TransactionCreate(BaseModel):
    origin_account_id: int
    destination_account_id: int
    amount: Decimal

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        return v


class TransactionOut(BaseModel):
    id: int
    origin_account_id: int
    destination_account_id: int
    amount: Decimal
    timestamp: datetime
    status: str

    class Config:
        from_attributes = True