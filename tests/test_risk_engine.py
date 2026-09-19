from decimal import Decimal
from datetime import datetime, timezone

from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.risk_rule import RiskRule
from app.services.risk_engine import evaluate_transaction
from app.services.auth import hash_password


def _create_user_and_account(db_session, balance=Decimal("10000")):
    user = User(email="test@test.com", password_hash=hash_password("1234567"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    account = Account(user_id=user.id, balance=balance)
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return user, account


def test_monto_alto_triggers_alert(db_session):
    _, origin = _create_user_and_account(db_session)
    destination = Account(user_id=origin.user_id, balance=Decimal("0"))
    db_session.add(destination)
    db_session.commit()
    db_session.refresh(destination)

    rule = RiskRule(name="monto_alto", threshold=Decimal("500"), active=True)
    db_session.add(rule)
    db_session.commit()

    transaction = Transaction(
        origin_account_id=origin.id,
        destination_account_id=destination.id,
        amount=Decimal("2000"),
        status="completed",
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)

    alerts = evaluate_transaction(db_session, transaction)

    assert len(alerts) == 1
    assert alerts[0].severity == "high"
    assert transaction.status == "flagged"


def test_transaction_below_threshold_does_not_trigger(db_session):
    _, origin = _create_user_and_account(db_session)
    destination = Account(user_id=origin.user_id, balance=Decimal("0"))
    db_session.add(destination)
    db_session.commit()
    db_session.refresh(destination)

    rule = RiskRule(name="monto_alto", threshold=Decimal("500"), active=True)
    db_session.add(rule)
    db_session.commit()

    transaction = Transaction(
        origin_account_id=origin.id,
        destination_account_id=destination.id,
        amount=Decimal("100"),
        status="completed",
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)

    alerts = evaluate_transaction(db_session, transaction)

    assert len(alerts) == 0
    assert transaction.status == "completed"


def test_inactive_rule_does_not_trigger(db_session):
    _, origin = _create_user_and_account(db_session)
    destination = Account(user_id=origin.user_id, balance=Decimal("0"))
    db_session.add(destination)
    db_session.commit()
    db_session.refresh(destination)

    rule = RiskRule(name="monto_alto", threshold=Decimal("500"), active=False)
    db_session.add(rule)
    db_session.commit()

    transaction = Transaction(
        origin_account_id=origin.id,
        destination_account_id=destination.id,
        amount=Decimal("2000"),
        status="completed",
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)

    alerts = evaluate_transaction(db_session, transaction)

    assert len(alerts) == 0