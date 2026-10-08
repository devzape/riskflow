from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.alert import Alert
from app.models.transaction import Transaction
from app.models.risk_rule import RiskRule
from app.schemas.alert import AlertOut, AlertExplanation
from app.services.ai_explainer import explain_alert

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=List[AlertOut])
def list_alerts(db: Session = Depends(get_db)):
    return db.query(Alert).order_by(Alert.created_at.desc()).all()


@router.get("/{alert_id}/explain", response_model=AlertExplanation)
def explain_alert_endpoint(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")

    transaction = db.query(Transaction).filter(Transaction.id == alert.transaction_id).first()
    rule = db.query(RiskRule).filter(RiskRule.id == alert.rule_id).first()

    transaction_data = {
        "amount": str(transaction.amount),
        "origin_account_id": transaction.origin_account_id,
        "destination_account_id": transaction.destination_account_id,
        "timestamp": transaction.timestamp.isoformat(),
    }
    rule_data = {
        "name": rule.name,
        "description": rule.description,
        "threshold": str(rule.threshold),
    }

    explanation = explain_alert(transaction_data, rule_data)
    return {"alert_id": alert_id, "explanation": explanation}