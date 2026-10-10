# 银行服务系统

一个简单的银行存款服务系统，基于 FastAPI + SQLite + SQLAlchemy 构建。

## 功能特性

- ✅ 开户（创建账户）
- ✅ 查询余额
- ✅ 存款
- ✅ 取款
- ✅ 转账（生成双交易记录）
- ✅ 查询交易历史
- ✅ 统一错误处理（400/404）

## 技术栈

- **Web 框架**: FastAPI
- **数据库**: SQLite
- **ORM**: SQLAlchemy
- **数据验证**: Pydantic
- **服务器**: Uvicorn

## 项目结构

```
src/001-bank-service/
├── requirements.txt    # Python 依赖
├── database.py         # 数据库配置与 Session 管理
├── models.py           # SQLAlchemy 数据模型（Account, Transaction）
├── schemas.py          # Pydantic 请求/响应模型
├── services.py         # 业务逻辑层
├── main.py             # FastAPI 入口与路由定义
└── client_test.py      # 客户端测试脚本
```

## 快速开始

### 1. 安装依赖

```powershell
cd src/001-bank-service
pip install -r requirements.txt
```

### 2. 启动服务

```powershell
python main.py
```

服务将在 `http://localhost:8000` 启动。

### 3. 访问 API 文档

打开浏览器访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. 运行测试

```powershell
python client_test.py
```

该脚本会自动执行以下测试：
1. 创建两个账户（张三、李四）
2. 存款操作
3. 取款操作
4. 转账操作
5. 查询交易历史
6. 错误场景测试（余额不足、账户不存在等）

## API 接口说明

| 方法 | 路径 | 描述 |
|------|------|------|
| `POST` | `/accounts` | 创建账户 |
| `GET` | `/accounts/{account_id}` | 查询账户余额 |
| `POST` | `/accounts/{account_id}/deposit` | 存款 |
| `POST` | `/accounts/{account_id}/withdraw` | 取款 |
| `POST` | `/accounts/{account_id}/transfer` | 转账 |
| `GET` | `/accounts/{account_id}/transactions` | 查询交易历史 |

## 数据模型

### Account（账户）

| 字段 | 类型 | 说明 |
|------|------|------|
| account_id | String(36) | UUID 账户号 |
| owner_name | String(100) | 户名 |
| balance | Numeric(19,4) | 余额（Decimal 精度）|
| created_at | DateTime | 开户时间 |

### Transaction（交易记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 自增主键 |
| account_id | String(36) | 所属账户 |
| transaction_type | String(20) | 类型：DEPOSIT/WITHDRAW/TRANSFER_OUT/TRANSFER_IN |
| amount | Numeric(19,4) | 金额 |
| related_account_id | String(36) | 关联账户（转账时填写）|
| transaction_group_id | String(36) | 交易组 ID（同一笔转账的两条记录共享）|
| created_at | DateTime | 交易时间 |

## 错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|------------|------|
| ACCOUNT_NOT_FOUND | 404 | 账户不存在 |
| INSUFFICIENT_FUNDS | 400 | 余额不足 |
| INVALID_TRANSFER | 400 | 无效转账（如向自己转账）|

## 注意事项

- 转账操作会生成**两条交易记录**（转出方 TRANSFER_OUT + 转入方 TRANSFER_IN），通过 `transaction_group_id` 关联
- 金额使用 `Decimal` 类型存储，避免浮点精度问题
- 数据库文件为 `bank.db`，位于项目根目录
