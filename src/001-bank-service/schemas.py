from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional, List


class AccountCreate(BaseModel):
    owner_name: str = Field(..., min_length=1, max_length=100)


class AccountResponse(BaseModel):
    account_id: str
    owner_name: str
    balance: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class DepositRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)


class WithdrawRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)


class TransferRequest(BaseModel):
    to_account_id: str
    amount: Decimal = Field(..., gt=0)


class TransactionResponse(BaseModel):
    id: int
    account_id: str
    transaction_type: str
    amount: Decimal
    related_account_id: Optional[str] = None
    transaction_group_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
