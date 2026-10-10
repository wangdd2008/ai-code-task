from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String(36), unique=True, index=True, nullable=False, default=generate_uuid)
    owner_name = Column(String(100), nullable=False)
    balance = Column(Numeric(19, 4), default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String(36), ForeignKey("accounts.account_id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)
    amount = Column(Numeric(19, 4), nullable=False)
    related_account_id = Column(String(36), nullable=True)
    transaction_group_id = Column(String(36), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    account = relationship("Account", back_populates="transactions")
