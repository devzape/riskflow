from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.alert import Alert
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.risk_rule import RiskRule
from app.models.user import User
from app.schemas.alert import AlertOut, AlertExplanation
from app.services.ai_explainer import explain_alert
from app.services.deps import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=List[AlertOut])
def list_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account_ids = [a.id for a in db.query(Account).filter(Account.user_id == current_user.id).all()]
    return (
        db.query(Alert)
        .join(Transaction, Alert.transaction_id == Transaction.id)
        .filter(Transaction.origin_account_id.in_(account_ids))
        .order_by(Alert.created_at.desc())
        .all()
    )


@router.get("/{alert_id}/explain", response_model=AlertExplanation)
async def explain_alert_endpoint(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")

    transaction = db.query(Transaction).filter(Transaction.id == alert.transaction_id).first()

    origin_account = db.query(Account).filter(Account.id == transaction.origin_account_id).first()
    if origin_account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tenés acceso a esta alerta")

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

    explanation = await explain_alert(transaction_data, rule_data)
    return {"alert_id": alert_id, "explanation": explanation}