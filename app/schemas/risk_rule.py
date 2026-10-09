from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, field_validator

# Solo estos nombres tienen lógica en el motor (app/services/risk_engine.py).
# Si agregás una regla nueva al motor, sumá su nombre acá.
RuleName = Literal["monto_alto", "frecuencia_sospechosa"]


def _validate_positive(v: Optional[Decimal]) -> Optional[Decimal]:
    if v is not None and v <= 0:
        raise ValueError("El umbral debe ser mayor a 0")
    return v


class RiskRuleCreate(BaseModel):
    name: RuleName
    description: Optional[str] = None
    threshold: Decimal
    active: bool = True

    @field_validator("threshold")
    @classmethod
    def threshold_must_be_positive(cls, v: Decimal) -> Decimal:
        return _validate_positive(v)


class RiskRuleUpdate(BaseModel):
    description: Optional[str] = None
    threshold: Optional[Decimal] = None
    active: Optional[bool] = None

    @field_validator("threshold")
    @classmethod
    def threshold_must_be_positive(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        return _validate_positive(v)


class RiskRuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    threshold: Decimal
    active: bool