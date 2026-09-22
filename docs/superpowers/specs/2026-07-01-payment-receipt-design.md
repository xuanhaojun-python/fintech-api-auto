# 交易凭证接口设计文档

**日期：** 2026-07-01
**模块：** payment（支付）
**状态：** 已审批

---

## 背景

在支付模块中新增交易凭证相关接口，支持用户查看和下载指定交易的凭证文件。

---

## 新增接口

### 1. 查看交易凭证

| 属性 | 值 |
|------|-----|
| 方法 | GET |
| 路径 | `/v1/txn/receipt/{txnId}` |
| Header | `X-ON-BEHALF-OF`（可选，代表操作的账户标识） |
| 成功响应 | 200，含凭证详情数据 |
| 失败场景 | txnId 不存在返回业务错误；缺少必要 Header 返回 400/422 |

### 2. 下载交易凭证

| 属性 | 值 |
|------|-----|
| 方法 | POST |
| 路径 | `/v1/txn/receipt/download/{txnId}` |
| Header | `X-ON-BEHALF-OF`（可选，代表操作的账户标识） |
| 成功响应 | 200，返回文件流或下载链接 |
| 失败场景 | txnId 不存在返回业务错误 |

---

## API 层变更

**文件：** `api/payment_api.py`

新增两个方法：

```python
def get_receipt(self, txn_id: str, on_behalf_of: str = None):
    """查看交易凭证"""
    headers = {"X-ON-BEHALF-OF": on_behalf_of} if on_behalf_of else {}
    return self.get(f"/v1/txn/receipt/{txn_id}", headers=headers)

def download_receipt(self, txn_id: str, on_behalf_of: str = None):
    """下载交易凭证"""
    headers = {"X-ON-BEHALF-OF": on_behalf_of} if on_behalf_of else {}
    return self.post(f"/v1/txn/receipt/download/{txn_id}", headers=headers)
```

`X-ON-BEHALF-OF` 通过 `request()` 方法的 `headers` 参数传入，与现有签名机制兼容（`build_sign_headers` 生成的签名头会 merge 进去）。

---

## 测试层变更

**文件：** `tests/test_payment_flow.py`

新增测试类 `TestReceiptFlow`，包含以下用例：

| 用例 ID | 用例名 | 类型 | 说明 |
|---------|--------|------|------|
| TC-PAY-RCP-001 | test_get_receipt_success | smoke | 查看已存在 txnId 的凭证，断言 200 且 data 非空 |
| TC-PAY-RCP-002 | test_get_receipt_nonexistent | regression | txnId 不存在，断言业务错误码 |
| TC-PAY-RCP-003 | test_get_receipt_missing_on_behalf_of | regression | 不传 X-ON-BEHALF-OF，验证接口行为（若为必填则返回 400/422） |
| TC-PAY-RCP-004 | test_download_receipt_success | smoke | 下载已存在 txnId 的凭证，断言 200 |
| TC-PAY-RCP-005 | test_download_receipt_nonexistent | regression | txnId 不存在，断言业务错误码 |

---

## 不在范围内

- 不新增测试文件（复用 `test_payment_flow.py`）
- 不修改 `base_client.py` 签名逻辑
- 不处理凭证内容解析（仅验证 HTTP 状态码和业务码）
