from sqlalchemy import Column, Integer, String, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class RiskRule(Base):
    __tablename__ = "risk_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    threshold = Column(Numeric(12, 2), nullable=False)
    active = Column(Boolean, default=True)

    alerts = relationship("Alert", back_populates="rule")