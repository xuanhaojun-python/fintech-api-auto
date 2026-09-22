# 交易凭证接口 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在支付模块新增查看凭证（GET）和下载凭证（POST）两个接口方法及对应测试用例。

**Architecture:** 在 `api/payment_api.py` 的 `PaymentAPI` 类中新增两个方法；测试用例追加到 `tests/test_payment_flow.py`，新增 `TestReceiptFlow` 类；`X-ON-BEHALF-OF` 通过 `headers` 参数传入，与现有签名机制兼容。

**Tech Stack:** Python、pytest、requests、现有 `BaseClient` / `assert_success`

---

### Task 1: 新增 API 方法

**Files:**
- Modify: `api/payment_api.py`

- [ ] **Step 1: 在 `payment_api.py` 末尾追加两个方法**

在文件最后一行（`get_txn` 方法）之后添加：

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

- [ ] **Step 2: 语法验证**

```bash
python -c "from api.payment_api import PaymentAPI; print('OK')"
```

期望输出：`OK`

- [ ] **Step 3: Commit**

```bash
git add api/payment_api.py
git commit -m "feat: add get_receipt and download_receipt to PaymentAPI"
```

---

### Task 2: 新增测试用例

**Files:**
- Modify: `tests/test_payment_flow.py`

- [ ] **Step 1: 在 `test_payment_flow.py` 末尾追加 `TestReceiptFlow` 类**

```python
class TestReceiptFlow:
    """交易凭证：查看与下载"""

    @pytest.mark.smoke
    def test_get_receipt_success(self, payment_api, merchant_order_id):
        """TC-PAY-RCP-001 查看已存在交易的凭证"""
        resp = payment_api.get_receipt(merchant_order_id)
        body = assert_success(resp)
        assert body.get("data"), "凭证 data 不应为空"

    @pytest.mark.regression
    def test_get_receipt_nonexistent(self, payment_api):
        """TC-PAY-RCP-002 查看不存在的 txnId，返回业务错误"""
        resp = payment_api.get_receipt("nonexistent_txn_99999")
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != "0000", \
            "不存在的 txnId 应返回业务错误"

    @pytest.mark.regression
    def test_get_receipt_missing_on_behalf_of(self, payment_api, merchant_order_id):
        """TC-PAY-RCP-003 不传 X-ON-BEHALF-OF，验证接口正常响应或返回参数错误"""
        resp = payment_api.get_receipt(merchant_order_id, on_behalf_of=None)
        assert resp.status_code in [200, 400, 422], \
            f"未预期状态码: {resp.status_code}"

    @pytest.mark.smoke
    def test_download_receipt_success(self, payment_api, merchant_order_id):
        """TC-PAY-RCP-004 下载已存在交易的凭证"""
        resp = payment_api.download_receipt(merchant_order_id)
        assert resp.status_code == 200, \
            f"期望 200，实际 {resp.status_code}，响应：{resp.text[:200]}"

    @pytest.mark.regression
    def test_download_receipt_nonexistent(self, payment_api):
        """TC-PAY-RCP-005 下载不存在的 txnId，返回业务错误"""
        resp = payment_api.download_receipt("nonexistent_txn_99999")
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != "0000", \
            "不存在的 txnId 应返回业务错误"
```

- [ ] **Step 2: 运行新增测试（smoke 用例）**

```bash
pytest tests/test_payment_flow.py::TestReceiptFlow -v -m smoke
```

期望：`test_get_receipt_success` 和 `test_download_receipt_success` 结果视环境而定（有数据则 PASS，无数据则 FAIL 并显示断言信息，不应出现 ImportError 或语法错误）

- [ ] **Step 3: 运行全部新增用例**

```bash
pytest tests/test_payment_flow.py::TestReceiptFlow -v
```

期望：5 个用例全部执行，无 ImportError / SyntaxError

- [ ] **Step 4: Commit**

```bash
git add tests/test_payment_flow.py
git commit -m "test: add TestReceiptFlow for get_receipt and download_receipt"
```
