import logging
import os
from logging.handlers import TimedRotatingFileHandler

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import engine, Base, get_db

# 配置日志：控制台 + 按日期分割的文件
log_dir = os.path.join(os.path.dirname(__file__), "log")
os.makedirs(log_dir, exist_ok=True)

log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.StreamHandler(),
        TimedRotatingFileHandler(
            filename=os.path.join(log_dir, "bank_service.log"),
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8"
        )
    ]
)
from models import Account
from schemas import (
    AccountCreate, AccountResponse, DepositRequest,
    WithdrawRequest, TransferRequest, TransactionResponse
)
from services import (
    create_account, get_account, deposit, withdraw,
    transfer, get_transactions, BankException
)

# \u521b\u5efa\u6570\u636e\u5e93\u8868
Base.metadata.create_all(bind=engine)

app = FastAPI(title="\u94f6\u884c\u670d\u52a1\u7cfb\u7edf", version="1.0.0")


@app.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account_endpoint(request: AccountCreate, db: Session = Depends(get_db)):
    account = create_account(db, request.owner_name)
    return account


@app.get("/accounts/{account_id}", response_model=AccountResponse)
def get_account_endpoint(account_id: str, db: Session = Depends(get_db)):
    account = get_account(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "ACCOUNT_NOT_FOUND", "message": f"\u8d26\u6237 {account_id} \u4e0d\u5b58\u5728"}
        )
    return account


@app.post("/accounts/{account_id}/deposit", response_model=AccountResponse)
def deposit_endpoint(account_id: str, request: DepositRequest, db: Session = Depends(get_db)):
    try:
        return deposit(db, account_id, request.amount)
    except BankException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.error_code, "message": e.message}
        )


@app.post("/accounts/{account_id}/withdraw", response_model=AccountResponse)
def withdraw_endpoint(account_id: str, request: WithdrawRequest, db: Session = Depends(get_db)):
    try:
        return withdraw(db, account_id, request.amount)
    except BankException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.error_code, "message": e.message}
        )


@app.post("/accounts/{account_id}/transfer")
def transfer_endpoint(account_id: str, request: TransferRequest, db: Session = Depends(get_db)):
    try:
        from_account, to_account = transfer(db, account_id, request.to_account_id, request.amount)
        return {
            "message": "\u8f6c\u8d26\u6210\u529f",
            "from_account": {"account_id": from_account.account_id, "balance": from_account.balance},
            "to_account": {"account_id": to_account.account_id, "balance": to_account.balance}
        }
    except BankException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.error_code, "message": e.message}
        )


@app.get("/accounts/{account_id}/transactions", response_model=List[TransactionResponse])
def get_transactions_endpoint(account_id: str, db: Session = Depends(get_db)):
    try:
        return get_transactions(db, account_id)
    except BankException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.error_code, "message": e.message}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
