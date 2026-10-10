#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
银行服务系统 - 命令行客户端
直接连接数据库进行查询操作
"""

import sys
import os

# 确保数据库路径正确：cli_client.py 与 bank.db 同目录
_current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_current_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Account, Transaction
from database import SessionLocal


def print_header(title):
    """打印分隔标题"""
    print(f"\n{'=' * 50}")
    print(f" {title}")
    print(f"{'=' * 50}")


def print_menu():
    """打印主菜单"""
    print_header("银行服务系统 - 命令行客户端")
    print("\n请选择操作：")
    print("  1. 查询所有账户")
    print("  2. 查询指定账户信息")
    print("  3. 查询账户交易记录")
    print("  4. 按持有人姓名搜索账户")
    print("  0. 退出")
    print("-" * 50)


def get_db_session():
    """获取数据库会话"""
    return SessionLocal()


def query_all_accounts():
    """查询所有账户"""
    print_header("所有账户列表")
    db = get_db_session()
    try:
        accounts = db.query(Account).all()
        if not accounts:
            print("  暂无账户记录")
            return

        print(f"\n  {'序号':<6}{'账户ID':<38}{'持有人':<12}{'余额':<15}{'创建时间'}")
        print("  " + "-" * 80)
        for idx, acc in enumerate(accounts, 1):
            print(
                f"  {idx:<6}{acc.account_id:<38}{acc.owner_name:<12}{str(acc.balance):<15}{acc.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n  共 {len(accounts)} 个账户")
    finally:
        db.close()


def query_account_detail():
    """查询指定账户详情"""
    print_header("查询账户详情")
    account_id = input("请输入账户ID: ").strip()
    if not account_id:
        print("  [错误] 账户ID不能为空")
        return

    db = get_db_session()
    try:
        account = db.query(Account).filter(Account.account_id == account_id).first()
        if not account:
            print(f"  [错误] 账户 {account_id} 不存在")
            return

        print(f"\n  账户ID:      {account.account_id}")
        print(f"  持有人姓名:  {account.owner_name}")
        print(f"  余额:        {account.balance} 元")
        print(f"  创建时间:    {account.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    finally:
        db.close()


def query_account_transactions():
    """查询账户交易记录"""
    print_header("查询账户交易记录")
    account_id = input("请输入账户ID: ").strip()
    if not account_id:
        print("  [错误] 账户ID不能为空")
        return

    db = get_db_session()
    try:
        account = db.query(Account).filter(Account.account_id == account_id).first()
        if not account:
            print(f"  [错误] 账户 {account_id} 不存在")
            return

        transactions = db.query(Transaction).filter(
            Transaction.account_id == account_id
        ).order_by(Transaction.created_at.desc()).all()

        print(f"\n  账户ID:   {account_id}")
        print(f"  持有人:   {account.owner_name}")
        print(f"  当前余额: {account.balance} 元")
        print(f"\n  交易记录:")

        if not transactions:
            print("    暂无交易记录")
            return

        print(f"  {'序号':<6}{'类型':<14}{'金额':<12}{'对方账户':<38}{'交易组ID':<38}{'时间'}")
        print("  " + "-" * 120)
        for idx, tx in enumerate(transactions, 1):
            related = tx.related_account_id if tx.related_account_id else "N/A"
            group = tx.transaction_group_id if tx.transaction_group_id else "N/A"
            tx_time = tx.created_at.strftime('%Y-%m-%d %H:%M:%S')
            print(f"  {idx:<6}{tx.transaction_type:<14}{str(tx.amount):<12}{related:<38}{group:<38}{tx_time}")

        print(f"\n  共 {len(transactions)} 条交易记录")
    finally:
        db.close()


def search_by_owner_name():
    """按持有人姓名搜索账户"""
    print_header("按持有人姓名搜索账户")
    keyword = input("请输入持有人姓名（支持模糊匹配）: ").strip()
    if not keyword:
        print("  [错误] 搜索关键词不能为空")
        return

    db = get_db_session()
    try:
        accounts = db.query(Account).filter(
            Account.owner_name.like(f"%{keyword}%")
        ).all()

        if not accounts:
            print(f"  未找到包含 '{keyword}' 的账户")
            return

        print(f"\n  搜索 '{keyword}' 的结果：")
        print(f"  {'序号':<6}{'账户ID':<38}{'持有人':<12}{'余额':<15}{'创建时间'}")
        print("  " + "-" * 80)
        for idx, acc in enumerate(accounts, 1):
            print(
                f"  {idx:<6}{acc.account_id:<38}{acc.owner_name:<12}{str(acc.balance):<15}{acc.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n  共 {len(accounts)} 个账户")
    finally:
        db.close()


def main():
    """主程序入口"""
    try:
        while True:
            print_menu()
            choice = input("请输入选项编号: ").strip()

            if choice == "0":
                print("\n感谢使用，再见！")
                sys.exit(0)
            elif choice == "1":
                query_all_accounts()
            elif choice == "2":
                query_account_detail()
            elif choice == "3":
                query_account_transactions()
            elif choice == "4":
                search_by_owner_name()
            else:
                print("\n[提示] 无效的选项，请重新输入")

            input("\n按回车键继续...")

    except KeyboardInterrupt:
        print("\n\n用户中断，程序退出")
        sys.exit(0)


if __name__ == "__main__":
    main()
