from unittest.mock import patch, AsyncMock
from decimal import Decimal
from app.models.alert import Alert
from app.models.risk_rule import RiskRule
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.user import User
from app.main import app
from app.services.deps import get_current_user  # Ajusta esta ruta si tu get_current_user está en otro archivo

@patch("app.routers.alerts.explain_alert", new_callable=AsyncMock)
def test_explain_alert_endpoint_mocked(mock_explain_alert, client, db_session):
    """
    Verifica que el endpoint devuelva la explicación sin llamar realmente a la API de Gemini.
    """
    explicacion_falsa = "Esta es una explicación simulada por el mock, sin usar internet."
    mock_explain_alert.return_value = explicacion_falsa

    user = User(email="mock_user@example.com", password_hash="123")
    db_session.add(user)
    db_session.commit()

    rule = RiskRule(name="test_rule", threshold=Decimal("100"), active=True)
    db_session.add(rule)
    db_session.commit()

    account = Account(user_id=user.id, balance=Decimal("1000")) 
    db_session.add(account)
    db_session.commit()

    tx = Transaction(
        origin_account_id=account.id, 
        destination_account_id=account.id, 
        amount=Decimal("500"), 
        status="flagged"
    )
    db_session.add(tx)
    db_session.commit()

    alert = Alert(transaction_id=tx.id, rule_id=rule.id, severity="high")
    db_session.add(alert)
    db_session.commit()
    db_session.refresh(alert)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.get(f"/alerts/{alert.id}/explain")


    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["alert_id"] == alert.id
    assert data["explanation"] == explicacion_falsa
    
    mock_explain_alert.assert_called_once()