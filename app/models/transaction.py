from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    origin_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    destination_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="completed")  # completed | flagged | reversed

    origin_account = relationship("Account", foreign_keys=[origin_account_id], back_populates="outgoing_transactions")
    destination_account = relationship("Account", foreign_keys=[destination_account_id], back_populates="incoming_transactions")
    alerts = relationship("Alert", back_populates="transaction")