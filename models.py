from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    fraud_probability = Column(Float)
    risk_score = Column(Integer)
    risk = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)