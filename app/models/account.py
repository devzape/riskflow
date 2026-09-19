from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    balance = Column(Numeric(12, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="accounts")
    outgoing_transactions = relationship(
        "Transaction", foreign_keys="Transaction.origin_account_id", back_populates="origin_account"
    )
    incoming_transactions = relationship(
        "Transaction", foreign_keys="Transaction.destination_account_id", back_populates="destination_account"
    )