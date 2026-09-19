from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionOut
from app.services.deps import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/", response_model=TransactionOut)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    origin = db.query(Account).filter(Account.id == data.origin_account_id).first()
    destination = db.query(Account).filter(Account.id == data.destination_account_id).first()

    if not origin or not destination:
        raise HTTPException(status_code=404, detail="Cuenta origen o destino no encontrada")

    if origin.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="La cuenta origen no te pertenece")

    if origin.balance < data.amount:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")

    origin.balance -= data.amount
    destination.balance += data.amount

    transaction = Transaction(
        origin_account_id=origin.id,
        destination_account_id=destination.id,
        amount=data.amount,
        status="completed",
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.get("/", response_model=List[TransactionOut])
def list_my_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account_ids = [a.id for a in db.query(Account).filter(Account.user_id == current_user.id).all()]
    return (
        db.query(Transaction)
        .filter(
            (Transaction.origin_account_id.in_(account_ids))
            | (Transaction.destination_account_id.in_(account_ids))
        )
        .all()
    )