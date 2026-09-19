from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertOut

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/", response_model=List[AlertOut])
def list_alerts(db: Session = Depends(get_db)):
    return db.query(Alert).order_by(Alert.created_at.desc()).all()