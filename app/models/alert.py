from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("risk_rules.id"), nullable=False)
    severity = Column(String, default="low")  # low | medium | high
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved = Column(Boolean, default=False)

    transaction = relationship("Transaction", back_populates="alerts")
    rule = relationship("RiskRule", back_populates="alerts")