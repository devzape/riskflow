from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.models.risk_rule import RiskRule
from app.models.transaction import Transaction
from app.models.alert import Alert


def evaluate_transaction(db: Session, transaction: Transaction) -> list[Alert]:
    """Evalúa una transacción contra todas las reglas activas y crea alertas si corresponde."""
    active_rules = db.query(RiskRule).filter(RiskRule.active == True).all()
    triggered_alerts = []

    for rule in active_rules:
        if _rule_triggers(db, rule, transaction):
            severity = _calculate_severity(rule, transaction)
            alert = Alert(
                transaction_id=transaction.id,
                rule_id=rule.id,
                severity=severity,
            )
            db.add(alert)
            triggered_alerts.append(alert)

    if triggered_alerts:
        transaction.status = "flagged"
        db.commit()
        for alert in triggered_alerts:
            db.refresh(alert)

    return triggered_alerts


def _rule_triggers(db: Session, rule: RiskRule, transaction: Transaction) -> bool:
    if rule.name == "monto_alto":
        return transaction.amount >= rule.threshold

    if rule.name == "frecuencia_sospechosa":
        window_start = datetime.now(timezone.utc) - timedelta(minutes=10)
        count = (
            db.query(Transaction)
            .filter(
                Transaction.origin_account_id == transaction.origin_account_id,
                Transaction.timestamp >= window_start,
            )
            .count()
        )
        return count >= rule.threshold

    return False


def _calculate_severity(rule: RiskRule, transaction: Transaction) -> str:
    if rule.name == "monto_alto":
        if transaction.amount >= rule.threshold * 3:
            return "high"
        elif transaction.amount >= rule.threshold * 1.5:
            return "medium"
        return "low"
    return "medium"