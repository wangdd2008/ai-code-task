"""
银行服务系统 - 客户端测试脚本
用于验证 API 接口的基本功能
"""
import requests
import json
from decimal import Decimal

BASE_URL = "http://localhost:8000"


def print_separator(title):
    print(f"\n{'=' * 50}")
    print(f" {title}")
    print(f"{'=' * 50}")


def create_account(owner_name: str):
    """开户"""
    url = f"{BASE_URL}/accounts"
    data = {"owner_name": owner_name}
    response = requests.post(url, json=data)
    result = response.json()
    print(f"开户 [{owner_name}]: {json.dumps(result, ensure_ascii=False, indent=2)}")
    return result["account_id"]


def get_account(account_id: str):
    """查询账户余额"""
    url = f"{BASE_URL}/accounts/{account_id}"
    response = requests.get(url)
    result = response.json()
    print(f"查询余额: {json.dumps(result, ensure_ascii=False, indent=2)}")
    return result


def deposit(account_id: str, amount: float):
    """存款"""
    url = f"{BASE_URL}/accounts/{account_id}/deposit"
    data = {"amount": amount}
    response = requests.post(url, json=data)
    result = response.json()
    print(f"存款 {amount} 元: {json.dumps(result, ensure_ascii=False, indent=2)}")
    return result


def withdraw(account_id: str, amount: float):
    """取款"""
    url = f"{BASE_URL}/accounts/{account_id}/withdraw"
    data = {"amount": amount}
    response = requests.post(url, json=data)
    result = response.json()
    print(f"取款 {amount} 元: {json.dumps(result, ensure_ascii=False, indent=2)}")
    return result


def transfer(from_account_id: str, to_account_id: str, amount: float):
    """转账"""
    url = f"{BASE_URL}/accounts/{from_account_id}/transfer"
    data = {"to_account_id": to_account_id, "amount": amount}
    response = requests.post(url, json=data)
    result = response.json()
    print(f"转账 {amount} 元: {json.dumps(result, ensure_ascii=False, indent=2)}")
    return result


def get_transactions(account_id: str):
    """查询交易历史"""
    url = f"{BASE_URL}/accounts/{account_id}/transactions"
    response = requests.get(url)
    result = response.json()
    print(f"交易历史 (共 {len(result)} 条):")
    for tx in result:
        print(f"  - [{tx['transaction_type']}] 金额: {tx['amount']} 元, "
              f"对方账户: {tx.get('related_account_id', 'N/A')}, "
              f"交易组ID: {tx['transaction_group_id']}")
    return result


def test_error_cases():
    """测试错误场景"""
    print_separator("错误场景测试")

    # 1. 查询不存在的账户
    print("\n1. 查询不存在的账户:")
    response = requests.get(f"{BASE_URL}/accounts/non-existent-id")
    print(f"   状态码: {response.status_code}, 响应: {response.json()}")

    # 2. 余额不足取款
    print("\n2. 余额不足取款:")
    # 先创建一个空账户
    empty_account = create_account("空账户用户")
    response = requests.post(
        f"{BASE_URL}/accounts/{empty_account}/withdraw",
        json={"amount": 100}
    )
    print(f"   状态码: {response.status_code}, 响应: {response.json()}")

    # 3. 向不存在的账户转账
    print("\n3. 向不存在的账户转账:")
    some_account = create_account("测试用户")
    response = requests.post(
        f"{BASE_URL}/accounts/{some_account}/transfer",
        json={"to_account_id": "fake-id", "amount": 50}
    )
    print(f"   状态码: {response.status_code}, 响应: {response.json()}")


def main():
    print("银行服务系统 - 客户端测试")
    print("请确保服务已启动: python main.py")

    # 检查服务是否在线
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=2)
        if response.status_code == 200:
            print("服务状态: 在线")
        else:
            print("服务状态: 异常")
            return
    except requests.exceptions.ConnectionError:
        print(f"无法连接到 {BASE_URL}，请确保服务已启动")
        return

    # ========== 基础功能测试 ==========
    print_separator("基础功能测试")

    # 1. 创建两个账户
    print("\n1. 创建账户:")
    account_a = create_account("张三")
    account_b = create_account("李四")

    # 2. 存款
    print("\n2. 存款:")
    deposit(account_a, 1000)
    deposit(account_b, 500)

    # 3. 查询余额
    print("\n3. 查询余额:")
    get_account(account_a)
    get_account(account_b)

    # 4. 取款
    print("\n4. 取款:")
    withdraw(account_a, 200)

    # 5. 转账
    print("\n5. 转账 (张三 -> 李四 300元):")
    transfer(account_a, account_b, 300)

    # 6. 查询最终余额
    print("\n6. 最终余额:")
    get_account(account_a)
    get_account(account_b)

    # 7. 查询交易历史
    print("\n7. 交易历史:")
    print("\n张三的交易记录:")
    get_transactions(account_a)
    print("\n李四的交易记录:")
    get_transactions(account_b)

    # ========== 错误场景测试 ==========
    test_error_cases()

    print_separator("测试完成")


if __name__ == "__main__":
    main()
