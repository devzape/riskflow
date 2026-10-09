from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.risk_rule import RiskRule
from app.models.user import User
from app.schemas.risk_rule import RiskRuleCreate, RiskRuleOut, RiskRuleUpdate
from app.services.deps import get_current_user

router = APIRouter(prefix="/risk-rules", tags=["risk-rules"])


@router.post("/", response_model=RiskRuleOut)
def create_rule(
    data: RiskRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if db.query(RiskRule).filter(RiskRule.name == data.name).first():
        raise HTTPException(status_code=409, detail="Ya existe una regla con ese nombre")

    rule = RiskRule(**data.model_dump())
    db.add(rule)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe una regla con ese nombre")
    db.refresh(rule)
    return rule


@router.get("/", response_model=List[RiskRuleOut])
def list_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(RiskRule).all()


@router.patch("/{rule_id}", response_model=RiskRuleOut)
def update_rule(
    rule_id: int,
    data: RiskRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = db.query(RiskRule).filter(RiskRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Regla no encontrada")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)
    return rule