from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertOut, AlertExplanation
from app.services.ai_explainer import explain_alert

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=list[AlertOut])
def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retorna la lista de alertas ordenadas por fecha reciente con paginación."""
    return (
        db.query(Alert)
        .order_by(Alert.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{alert_id}/explain", response_model=AlertExplanation)
async def explain_alert_endpoint(alert_id: int, db: Session = Depends(get_db)):
    """Obtiene la explicación generada por IA para una alerta específica."""
    # Trae la alerta, su transacción y regla asociada en una sola consulta SQL (JOIN)
    alert = (
        db.query(Alert)
        .options(
            joinedload(Alert.transaction),
            joinedload(Alert.rule)
        )
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")

    # Validación preventiva de relaciones para evitar errores HTTP 500
    if not alert.transaction or not alert.rule:
        raise HTTPException(
            status_code=422,
            detail="La alerta no cuenta con una transacción o regla válida asociada",
        )

    transaction_data = {
        "amount": str(alert.transaction.amount),
        "origin_account_id": alert.transaction.origin_account_id,
        "destination_account_id": alert.transaction.destination_account_id,
        "timestamp": alert.transaction.timestamp.isoformat(),
    }
    rule_data = {
        "name": alert.rule.name,
        "description": alert.rule.description,
        "threshold": str(alert.rule.threshold),
    }

    # Llamada asíncrona a la función refactorizada con Gemini
    explanation = await explain_alert(transaction_data, rule_data)
    return {"alert_id": alert_id, "explanation": explanation}