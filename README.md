# fintech_api_auto

针对 **Planckage OpenAPI** 的接口自动化测试框架，基于 Python + pytest 构建，覆盖账户管理、智能支付、KYC/KYT 合规审核、出金、换汇、收款人、地址管理等核心业务模块。

---

## 目录

- [项目简介](#项目简介)
- [目录结构](#目录结构)
- [快速上手](#快速上手)
- [框架架构](#框架架构)
- [API 模块清单](#api-模块清单)
- [测试用例覆盖矩阵](#测试用例覆盖矩阵)
- [新增用例规范](#新增用例规范)

---

## 项目简介

| 项目 | 说明 |
|------|------|
| 覆盖系统 | Planckage OpenAPI（账户、支付、KYC、KYT、出金、换汇、收款人、地址、文件等） |
| 测试环境 | SIT / UAT / Dev |
| 认证方式 | ECDSA 签名（API Key + Secret） |
| 技术栈 | Python 3.10、pytest 7、requests、allure-pytest、colorlog、openpyxl |
| 报告格式 | Allure HTML + pytest-html |
| CI 集成 | Jenkinsfile（见根目录） |

---

## 目录结构

```
fintech_api_auto/
├── api/                        # API 客户端层（每个模块一个文件）
│   ├── base_client.py          # 统一 HTTP 客户端：签名、日志、重试
│   ├── account_api.py          # 账户管理接口
│   ├── payment_api.py          # 智能支付接口
│   ├── kyc_api.py              # KYC 接口
│   ├── kyt_api.py              # KYT 审核接口
│   ├── refund_api.py           # 退款接口
│   ├── withdraw_api.py         # 加密货币出金接口
│   ├── address_api.py          # 地址管理接口
│   ├── txn_api.py              # 交易查询接口
│   ├── quote_api.py            # 换汇询价接口
│   ├── beneficiary_api.py      # 收款人接口
│   ├── genius_api.py           # Genius 接口
│   ├── fee_api.py              # 费率配置接口
│   ├── file_api.py             # 文件上传接口（multipart）
│   ├── sales_api.py            # 销售数据查询接口
│   └── mock_api.py             # Mock 控制接口（仅测试环境）
│
├── service/                    # 业务服务层（复杂流程编排）
│   ├── payment_service.py      # 智能支付完整流程（标准支付 / Travel Rule 支付）
│   └── refund_service.py       # 退款完整流程（立即退款 / 延迟退款）
│
├── tests/                      # pytest 测试用例
│   ├── conftest.py             # session 级 fixture（API 客户端、Service、测试数据）
│   ├── test_account.py         # 账户状态查询、余额、创建 PDCA 账户
│   ├── test_payment_flow.py    # 智能支付流程、Travel Rule、入金/退款查询
│   ├── test_kyc.py             # KYC 信息提交与查询
│   ├── test_kyt.py             # KYT 审核（Approve/Reject/LN Case）
│   ├── test_refund.py          # 退款 Case 审核流程
│   ├── test_withdraw.py        # 加密货币出金
│   ├── test_address.py         # 地址分配、所有权 Case
│   ├── test_deposit_address.py # 入金地址 CRUD
│   ├── test_txn.py             # 充值/换汇/出金交易列表查询
│   ├── test_quote.py           # 换汇询价
│   ├── test_beneficiary.py     # 法币收款人创建
│   ├── test_genius.py          # Genius 购买配置与历史
│   ├── test_file_upload.py     # 文件上传
│   ├── test_sales.py           # 销售数据查询
│   └── test_create_pdca_with_kyc.py  # PDCA 账户 + KYC 联合流程
│
├── utils/
│   ├── logger.py               # 彩色控制台 + 按天滚动文件日志
│   ├── data_loader.py          # YAML / JSON / Excel 测试数据加载
│   ├── assertions.py           # 断言工具（assert_success / assert_error / assert_schema 等）
│   └── db_client.py            # 数据库查询工具（MySQL，用于 fixture 预置数据）
│
├── auth/
│   └── signer.py               # ECDSA 签名（build_sign_headers）
│
├── config/
│   ├── settings.py             # 从环境变量加载 BASE_URL / API_KEY / API_SECRET 等
│   └── environments.yaml       # 多环境配置（sit / uat / dev）
│
├── data/
│   ├── accounts.yaml           # 测试账户数据（各种状态）
│   └── payment_cases.yaml      # 支付流程数据驱动测试数据
│
├── schemas/                    # JSON Schema（用于响应结构校验）
│
├── reports/                    # 测试报告输出目录（gitignore）
│   ├── allure-results/
│   └── report.html
│
├── logs/                       # 运行日志（gitignore）
├── .env.example                # 环境变量模板
├── pytest.ini                  # pytest 配置（markers / addopts / testpaths）
└── Jenkinsfile                 # CI 流水线
```

---

## 快速上手

### 1. 前置依赖

```bash
# Python 3.10+
python --version

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入对应环境的账号信息：

```dotenv
TEST_ENV=sit                    # 目标环境：sit / uat / dev

SIT_USERNAME=your_sit_username
SIT_PASSWORD=your_sit_password
```

> `config/settings.py` 会根据 `TEST_ENV` 自动从 `environments.yaml` 加载 `BASE_URL`、`AUTH_URL`、`TIMEOUT` 等。API Key / Secret 从登录接口获取后注入环境变量，或直接在 `.env` 中配置 `API_KEY` / `API_SECRET`。

### 3. 运行测试

```bash
# 冒烟测试（P0 核心用例，快速回归）
pytest -m smoke

# 全量回归测试
pytest -m regression

# 安全测试
pytest -m security

# 性能测试
pytest -m performance

# 全量（包含无标记用例）
pytest

# 指定模块
pytest tests/test_account.py
pytest tests/test_payment_flow.py

# 指定单个用例
pytest tests/test_account.py::TestAccountStatusNormal::test_query_valid_account -v
```

### 4. 查看报告

```bash
# Allure 报告（需安装 allure 命令行工具）
allure serve reports/allure-results

# HTML 报告
open reports/report.html
```

---

## 框架架构

### 四层设计

```
┌─────────────────────────────────────────────┐
│  Test Layer（tests/）                        │
│  pytest 用例类 + fixture 注入                │
└────────────────┬────────────────────────────┘
                 │ 调用
┌────────────────▼────────────────────────────┐
│  Service Layer（service/）                  │
│  PaymentService / RefundService             │
│  编排多步业务流程                            │
└────────────────┬────────────────────────────┘
                 │ 调用
┌────────────────▼────────────────────────────┐
│  API Layer（api/）                          │
│  XxxAPI 类，每个方法对应一个接口             │
│  继承 BaseClient                            │
└────────────────┬────────────────────────────┘
                 │ 调用
┌────────────────▼────────────────────────────┐
│  BaseClient（api/base_client.py）           │
│  ECDSA 签名 · 请求日志 · 500 自动重试       │
└─────────────────────────────────────────────┘
```

### BaseClient 核心机制

- **ECDSA 签名**：每次请求前调用 `auth/signer.py::build_sign_headers`，对 `method + path + query + body` 签名，生成 `X-API-KEY`、`X-TIMESTAMP`、`X-SIGNATURE` 请求头。
- **请求日志**：成功请求记录 INFO（含耗时），失败记录 WARNING（含响应体前 300 字符）。
- **500 重试**：服务端错误自动重试一次（`_DEFAULT_RETRIES = 1`），间隔 0.5 秒。

### 多角色支持

`BaseClient(role=...)` 决定签名使用哪个账户的 API Key/Secret：

| role | 用途 |
|------|------|
| `merchant` | 商户主账户操作（创建账户、支付、KYC 等） |
| `risk` | 风控审核（KYT Case Approve/Reject） |
| `finance` | 财务审核（退款 Case Finance Review） |

### 数据驱动

`utils/data_loader.py` 支持从 `data/` 目录加载测试数据：

```python
from utils.data_loader import load_yaml, load_json, load_excel

# YAML
accounts = load_yaml("accounts.yaml")

# Excel（首行为表头，返回 list[dict]）
cases = load_excel("cases.xlsx", sheet_name="支付场景")
```

### Fixture 机制

`tests/conftest.py` 定义 session 级 fixture，所有 API 客户端和 Service 仅初始化一次：

```python
# 使用示例
def test_something(account_api, accounts):
    acc = accounts["valid"]
    resp = account_api.get_status(acc["externalAccountId"], acc["registeredEmail"])
```

数据库 fixture（如 `bene_id`、`merchant_order_id`）通过 `utils/db_client.py::query_one` 从 MySQL 预置数据。

---

## API 模块清单

| 模块 | 类名 | HTTP 路径前缀 | 核心方法 |
|------|------|--------------|---------|
| **账户管理** | `AccountAPI` | `/v1/account` | `create_account`、`create_pdca_account`、`create_pdca_individual_account`、`get_status`、`list_accounts`、`get_wallet_balance`、`update_account_status`、`charge_off_quote`、`wallet_exchange` |
| **智能支付** | `PaymentAPI` | `/v1/smart-payment` | `create_link`、`get_link_status`、`check_travel_rule`、`submit_travel_rule_info`、`get_payment_address`、`refund`、`get_refund`、`get_txn`、`get_receipt`、`download_receipt` |
| **KYC** | `KycAPI` | `/v1/kyc` | `create_kyc_basic`、`save_enterprise_kyc`、`save_individual_kyc`、`get_kyc_result` |
| **KYT** | `KytAPI` | `/v1/kyt` | `get_case`、`approve`、`reject`、`get_ln_cases`、`complete_ln_case`、`collect_travel_rule_info` |
| **退款** | `RefundAPI` | `/v1/refund` | `get_case`、`list_cases`、`risk_review`、`finance_review`、`get_refund_txn` |
| **出金** | `WithdrawAPI` | `/v1/withdraw` | `withdraw_crypto` |
| **换汇询价** | `QuoteAPI` | `/v1/quote` | `get_quote` |
| **收款人** | `BeneficiaryAPI` | `/v1/beneficiary`、`/v2/beneficiary` | `create_beneficiary`、`create_beneficiary_v2` |
| **地址管理** | `AddressAPI` | `/v1/addresses`、`/v1/address` | `allocate_address`、`release_address`、`create_ownership_case`、`check_address_ownership_eligibility`、`get_case_by_bene_id`、`create_deposit_address`、`get_deposit_address`、`list_deposit_addresses`、`delete_deposit_address`、`create_withdraw_address`、`dispatch_deposit_addresses`、`get_recharge_addresses` |
| **交易查询** | `TxnAPI` | `/v1/txns` | `get_deposit_txn`、`list_deposit_txns`（充值）、`list_fx_txns`（换汇）、`list_withdraw_txns`（出金） |
| **文件上传** | `FileAPI` | `/v1/file` | `upload_file`（multipart/form-data） |
| **Genius** | `GeniusAPI` | `/v1/genius` | `get_purchase_conf`、`get_history` |
| **费率配置** | `FeeAPI` | `/v1/account/fee-config` | `get_fee_configs` |
| **销售数据** | `SalesAPI` | `/v1/sales` | `query_sales` |
| **Mock 控制** | `MockAPI` | `/v1/mock` | `set_travel_rule_result`、`set_ln_scan_result`、`simulate_chain_transaction` |

---

## 测试用例覆盖矩阵

| 测试文件 | 覆盖模块 | Smoke | Regression | Security | Performance | 总计 |
|---------|---------|------:|----------:|--------:|------------:|----:|
| `test_account.py` | 账户状态查询、余额查询、创建 PDCA 账户（企业/个人）、修改账户状态 | 7 | 23 | 1 | 2 | 46 |
| `test_payment_flow.py` | 智能支付全流程、Travel Rule、LN 命中、退款创建/查询、凭证查看/下载 | 8 | 27 | 0 | 0 | 38 |
| `test_kyc.py` | 创建企业 KYC、保存企业 KYC、保存个人 KYC、查询 KYC 结果 | 4 | 23 | 0 | 0 | 27 |
| `test_kyt.py` | KYT Case 查询、Approve、Reject、LN Case 排查、Travel Rule 信息采集 | 8 | 24 | 0 | 0 | 43 |
| `test_withdraw.py` | 加密货币出金（正常场景、异常场景、幂等性） | 1 | 29 | 0 | 0 | 30 |
| `test_refund.py` | 退款 Case 查询、风控审核、财务审核 | 5 | 25 | 0 | 0 | 34 |
| `test_address.py` | 地址分配/释放、地址所有权 Case | 10 | 29 | 0 | 0 | 39 |
| `test_deposit_address.py` | 入金地址 CRUD、分页查询、批量分配 | 4 | 35 | 0 | 0 | 39 |
| `test_txn.py` | 充值交易查询、换汇交易列表、出金交易列表 | 4 | 47 | 0 | 0 | 51 |
| `test_quote.py` | 换汇询价 | 1 | 14 | 0 | 0 | 15 |
| `test_beneficiary.py` | 法币收款人创建 V1/V2 | 1 | 12 | 0 | 0 | 13 |
| `test_genius.py` | Genius 购买配置查询、历史记录 | 1 | 9 | 0 | 0 | 10 |
| `test_file_upload.py` | 文件上传 | 1 | 0 | 0 | 0 | 1 |
| `test_sales.py` | 销售数据查询 | 1 | 15 | 0 | 0 | 16 |
| `test_create_pdca_with_kyc.py` | PDCA 账户创建 + KYC 联合流程 | 0 | 0 | 0 | 0 | 1 |
| **合计** | | **56** | **312** | **1** | **2** | **403** |

---

## 新增用例规范

### 新增 API 类

1. 在 `api/` 下创建 `xxx_api.py`，继承 `BaseClient`：

```python
from api.base_client import BaseClient

class XxxAPI(BaseClient):
    """Xxx 接口"""

    def do_something(self, param: str):
        """接口说明"""
        return self.post("/v1/xxx/action", json={"param": param})
```

2. 在 `tests/conftest.py` 添加 session 级 fixture：

```python
@pytest.fixture(scope="session")
def xxx_api():
    client = XxxAPI(role="merchant")
    yield client
    client.close()
```

### 新增测试用例

在对应的 `tests/test_xxx.py` 中，按以下结构编写：

```python
class TestXxxNormal:
    """正常场景"""

    @pytest.mark.smoke
    def test_xxx_success(self, xxx_api):
        """TC-XXX-001 正常场景描述
        前置条件：...
        预期结果：HTTP 200，code=0000，data 包含 xxxId
        """
        resp = xxx_api.do_something("valid_param")
        body = assert_success(resp)
        assert body.get("data", {}).get("xxxId"), "xxxId 不应为空"
        assert_response_time(resp, max_ms=2000)

class TestXxxAbnormal:
    """异常场景"""

    @pytest.mark.regression
    def test_xxx_missing_param(self, xxx_api):
        """TC-XXX-101 缺少必填参数，返回 400/422"""
        resp = xxx_api.post("/v1/xxx/action", json={})
        assert resp.status_code in [400, 422] or resp.json().get("code") != "0000"
```

### 命名约定

| 元素 | 规范 | 示例 |
|------|------|------|
| 用例 ID | `TC-{模块缩写}-{三位序号}` | `TC-AS-001`、`TC-KYC-IND-003` |
| 测试方法 | `test_{行为描述}` | `test_query_valid_account` |
| 测试类（正常） | `TestXxxNormal` | `TestAccountStatusNormal` |
| 测试类（异常） | `TestXxxAbnormal` | `TestWithdrawCryptoAbnormal` |
| 测试类（边界） | `TestXxxBoundary` | `TestAccountStatusBoundary` |

### Marker 使用规范

| Marker | 适用场景 | 运行命令 |
|--------|---------|---------|
| `@pytest.mark.smoke` | P0 核心路径，每次发版必跑 | `pytest -m smoke` |
| `@pytest.mark.regression` | 完整功能覆盖，全量回归 | `pytest -m regression` |
| `@pytest.mark.security` | SQL 注入、XSS、越权等安全场景 | `pytest -m security` |
| `@pytest.mark.performance` | 响应时间验证、并发压测 | `pytest -m performance` |

> 无 marker 的用例在任何运行模式下都会执行。

### 断言工具

优先使用 `utils/assertions.py` 中的工具函数，保持断言风格统一：

| 函数 | 用途 |
|------|------|
| `assert_success(resp)` | 断言 HTTP 200 且 code 为成功码，返回响应体 dict |
| `assert_error(resp, code)` | 断言返回指定业务错误码 |
| `assert_field(body, *keys)` | 断言嵌套字段存在且非空 |
| `assert_response_time(resp, max_ms)` | 断言响应时间不超过阈值 |
| `assert_account_status(body, status)` | 断言账户状态字段 |
| `assert_schema(body, schema)` | JSON Schema 结构校验 |
