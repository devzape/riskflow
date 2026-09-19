from pydantic import BaseModel
from decimal import Decimal

class RiskRuleCreate(BaseModel):
    name: str
    description: str | None = None
    threshold: Decimal
    active: bool = True

class RiskRuleOut(BaseModel):
    id: int
    name: str
    description: str | None
    threshold: Decimal
    active: bool

    class Config:
        from_attributes = True