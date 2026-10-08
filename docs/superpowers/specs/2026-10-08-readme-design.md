# 设计文档：项目 README 综合文档

**日期**：2026-10-08
**受众**：开发/测试工程师
**格式**：单文件中文 Markdown（`README.md`）

---

## 目标

将 fintech_api_auto 项目的所有关键信息整合成一份 README.md，让新加入的工程师能快速上手，让已有成员快速查阅接口/用例范围。

---

## 章节结构

### 1. 项目简介
- 项目定位：针对 Planckage OpenAPI 的接口自动化测试框架
- 覆盖系统：账户管理、智能支付、KYC、KYT、出金、换汇、收款人、地址管理、文件上传等
- 测试环境：SIT / UAT / Dev（`config/environments.yaml`）
- 技术栈：Python 3.10、pytest、requests、allure-pytest、colorlog

### 2. 目录结构
带注释的树形结构，覆盖：
- `api/`：各功能模块的 API 客户端类（继承 BaseClient）
- `service/`：复杂业务流程编排（PaymentService、RefundService）
- `tests/`：pytest 测试用例
- `utils/`：断言工具、日志、数据加载、数据库客户端
- `config/`：多环境配置和 Settings
- `data/`：YAML/Excel 测试数据
- `auth/`：ECDSA 签名模块

### 3. 快速上手
- 前置依赖：Python 3.10+，pip install -r requirements.txt
- 配置：复制 `.env.example` 为 `.env`，填入 TEST_ENV 和账号信息
- 运行命令：
  - 冒烟测试：`pytest -m smoke`
  - 回归测试：`pytest -m regression`
  - 全量：`pytest`
  - 指定模块：`pytest tests/test_account.py`
- 报告：Allure（`reports/allure-results`）+ HTML（`reports/report.html`）

### 4. 框架架构
- 四层设计：BaseClient → API 层 → Service 层 → Test 层
- BaseClient：统一 HTTP 请求、ECDSA 签名、请求日志、500 自动重试
- 多角色支持：merchant / risk / finance（决定签名 key 来源）
- 数据驱动：`utils/data_loader.py` 支持 YAML / JSON / Excel
- conftest.py：session 级 fixture，API 客户端和 Service 均在此初始化

### 5. API 模块清单
表格形式列出每个 API 类、HTTP 路径前缀、核心方法：

| 模块 | 类名 | 核心接口 |
|------|------|---------|
| 账户管理 | AccountAPI | 创建账户、查询状态、钱包余额、费率配置、修改状态等 |
| 智能支付 | PaymentAPI | 创建 Link、查询状态、Travel Rule 检查/提交、获取支付地址、退款、凭证 |
| KYC | KycAPI | 创建/保存企业 KYC、保存个人 KYC、查询结果 |
| KYT | KytAPI | 查询/审核 Case、LN 扫描 Case、Travel Rule 信息采集 |
| 退款 | RefundAPI | 查询 Case、列表查询、风控审核、财务审核 |
| 出金 | WithdrawAPI | 发起加密货币提款 |
| 换汇询价 | QuoteAPI | 换汇询价 |
| 收款人 | BeneficiaryAPI | 创建法币收款人 V1/V2 |
| 地址管理 | AddressAPI | 分配/释放地址、地址所有权 Case、入金/出金地址 CRUD |
| 交易查询 | TxnAPI | 充值/换汇/出金交易分页查询 |
| 文件上传 | FileAPI | multipart 文件上传 |
| Genius | GeniusAPI | 购买配置查询、历史记录 |
| 费率 | FeeAPI | 批量费率配置查询 |
| 销售数据 | SalesAPI | 销售数据查询 |
| Mock | MockAPI | Travel Rule Mock、LN 扫描 Mock、模拟链上到账 |

### 6. 测试用例覆盖矩阵
表格：测试文件 | 模块 | Smoke | Regression | Security | Performance | 总计

覆盖文件：
- test_account.py、test_payment_flow.py、test_kyc.py、test_kyt.py
- test_refund.py、test_withdraw.py、test_address.py、test_deposit_address.py
- test_txn.py、test_quote.py、test_beneficiary.py、test_genius.py
- test_file_upload.py、test_sales.py、test_create_pdca_with_kyc.py

### 7. 新增用例规范
- 新增 API 类：继承 BaseClient，文件放 `api/` 目录，类名 `XxxAPI`
- 新增 Fixture：在 `conftest.py` 添加 session 级 fixture
- 用例命名：`TC-{模块缩写}-{三位序号}`，如 `TC-AS-001`
- Marker：smoke（P0）、regression（全量）、security、performance
- 断言：使用 `utils/assertions.py` 中的工具函数（assert_success、assert_error、assert_schema 等）

---

## 约束

- 不生成 .venv 或第三方包内容
- 测试数据文件（`.env`）不放入文档
- 代码示例以最短能说明问题的片段为准
