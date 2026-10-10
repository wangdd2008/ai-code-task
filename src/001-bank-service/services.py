import logging
from sqlalchemy.orm import Session
from decimal import Decimal
from uuid import uuid4
from models import Account, Transaction

logger = logging.getLogger(__name__)


class BankException(Exception):
    def __init__(self, error_code: str, message: str):
        self.error_code = error_code
        self.message = message


def create_account(db: Session, owner_name: str) -> Account:
    account = Account(owner_name=owner_name, balance=Decimal("0"))
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def get_account(db: Session, account_id: str) -> Account:
    return db.query(Account).filter(Account.account_id == account_id).first()


def deposit(db: Session, account_id: str, amount: Decimal) -> Account:
    account = get_account(db, account_id)
    if not account:
        raise BankException("ACCOUNT_NOT_FOUND", f"\u8d26\u6237 {account_id} \u4e0d\u5b58\u5728")

    account.balance = Decimal(str(account.balance)) + amount

    transaction = Transaction(
        account_id=account_id,
        transaction_type="DEPOSIT",
        amount=amount,
        transaction_group_id=str(uuid4())
    )
    db.add(transaction)
    db.commit()
    db.refresh(account)
    return account


def withdraw(db: Session, account_id: str, amount: Decimal) -> Account:
    account = get_account(db, account_id)
    if not account:
        raise BankException("ACCOUNT_NOT_FOUND", f"\u8d26\u6237 {account_id} \u4e0d\u5b58\u5728")

    current_balance = Decimal(str(account.balance))
    if current_balance < amount:
        raise BankException("INSUFFICIENT_FUNDS", "\u4f59\u989d\u4e0d\u8db3")

    account.balance = current_balance - amount

    transaction = Transaction(
        account_id=account_id,
        transaction_type="WITHDRAW",
        amount=amount,
        transaction_group_id=str(uuid4())
    )
    db.add(transaction)
    db.commit()
    db.refresh(account)
    return account


def transfer(db: Session, from_account_id: str, to_account_id: str, amount: Decimal) -> tuple:
    from_account = get_account(db, from_account_id)
    if not from_account:
        raise BankException("ACCOUNT_NOT_FOUND", f"\u8f6c\u51fa\u8d26\u6237 {from_account_id} \u4e0d\u5b58\u5728")

    to_account = get_account(db, to_account_id)
    if not to_account:
        raise BankException("ACCOUNT_NOT_FOUND", f"\u8f6c\u5165\u8d26\u6237 {to_account_id} \u4e0d\u5b58\u5728")

    if from_account_id == to_account_id:
        raise BankException("INVALID_TRANSFER", "\u4e0d\u80fd\u5411\u540c\u4e00\u8d26\u6237\u8f6c\u8d26")

    from_balance = Decimal(str(from_account.balance))
    if from_balance < amount:
        raise BankException("INSUFFICIENT_FUNDS", "\u4f59\u989d\u4e0d\u8db3")

    group_id = str(uuid4())
    logger.info(f"[TRANSFER START] {from_account_id} -> {to_account_id}, amount={amount}, group_id={group_id}")

    # \u6263\u51cf\u8f6c\u51fa\u65b9\u4f59\u989d
    from_account.balance = from_balance - amount
    logger.info(f"[FROM ACCOUNT] {from_account_id} balance: {from_balance} -> {from_account.balance}")

    # \u589e\u52a0\u8f6c\u5165\u65b9\u4f59\u989d
    to_balance = Decimal(str(to_account.balance))
    to_account.balance = to_balance + amount
    logger.info(f"[TO ACCOUNT] {to_account_id} balance: {to_balance} -> {to_account.balance}")

    # \u521b\u5efa\u8f6c\u51fa\u65b9\u4ea4\u6613\u8bb0\u5f55
    out_transaction = Transaction(
        account_id=from_account_id,
        transaction_type="TRANSFER_OUT",
        amount=amount,
        related_account_id=to_account_id,
        transaction_group_id=group_id
    )
    db.add(out_transaction)
    logger.info(f"[TRANSFER_OUT] account={from_account_id}, group_id={group_id}")

    # 创建转入方交易记录（与转出方共享同一 transaction_group_id）
    in_transaction = Transaction(
        account_id=to_account_id,
        transaction_type="TRANSFER_IN",
        amount=amount,
        related_account_id=from_account_id,
        transaction_group_id=group_id
    )
    db.add(in_transaction)
    logger.info(f"[TRANSFER_IN] account={to_account_id}, group_id={group_id}")

    db.commit()
    logger.info(f"[TRANSFER COMMIT] group_id={group_id}")
    db.refresh(from_account)
    db.refresh(to_account)

    return from_account, to_account


def get_transactions(db: Session, account_id: str):
    account = get_account(db, account_id)
    if not account:
        raise BankException("ACCOUNT_NOT_FOUND", f"\u8d26\u6237 {account_id} \u4e0d\u5b58\u5728")

    return db.query(Transaction).filter(
        Transaction.account_id == account_id
    ).order_by(Transaction.created_at.desc()).all()
