from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.risk_rule import RiskRule
from app.models.user import User
from app.schemas.risk_rule import RiskRuleCreate, RiskRuleOut
from app.services.deps import get_current_user

router = APIRouter(prefix="/risk-rules", tags=["risk-rules"])

@router.post("/", response_model=RiskRuleOut)
def create_rule(
    data: RiskRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = RiskRule(**data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.get("/", response_model=List[RiskRuleOut])
def list_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(RiskRule).all()