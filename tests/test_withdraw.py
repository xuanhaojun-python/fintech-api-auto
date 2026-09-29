"""
加密货币提款接口测试
接口：POST /v1/withdraw/crypto
请求：ccy, amount, beneId, chain, requestId, verifiedData（可选）
Header：X-ON-BEHALF-OF（子账户 accountId）

实际响应结构：
{
  "code": "0000",
  "data": {
    "accountId": "ACC...",
    "txnId": "POT...",
    "status": "PROCESSING",
    "requestId": "req_...",
    "returnFee": true,
    "createdAt": 1790651441502,
    "withdrawalMoney": {"ccy": "USDT", "amount": "0.001000"},
    "payoutMoney":     {"ccy": "USDT", "amount": "0.001000"},
    "fee":             {"money": {"ccy": "USDT", "amount": "0.001000"}},
    "bene": {
      "destinationAddress": "0x...",
      "identifier": {
        "company": {"companyName": "..."},
        "tradingPlatformAccNo": "0x...",
        "proof": "uuid"
      }
    }
  }
}
"""
import uuid

import pytest

from utils.assertions import assert_success, assert_response_time

# 已验证的测试数据
WITHDRAW_ACCOUNT_ID = "ACC1996532313185505280"
VALID_BENE_ID = "CBENE1998225590502723584"
VALID_AMOUNT = "0.001"
VERIFIED_DATA = {"company": {"companyName": "Xuan Company"}}

# 属于其他账户的 beneId（用于跨账户校验）
OTHER_ACCOUNT_BENE_ID = "CBENE1814182199432450048"


def _req_id():
    """生成唯一 requestId"""
    return f"req_{uuid.uuid4().hex[:16]}"


class TestWithdrawCryptoNormal:
    """正常场景"""

    @pytest.mark.smoke
    def test_withdraw_crypto_success(self, withdraw_api):
        """TC-WITHDRAW-001 正常提款，返回成功
        前置条件：账户余额充足，beneId 有效
        预期结果：HTTP 200，code=0000，data 包含 txnId
        """
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            verified_data=VERIFIED_DATA,
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        print(f"\n[TC-WITHDRAW-001] {resp.status_code} {resp.json()}")
        body = assert_success(resp)
        assert body.get("data") is not None, f"data 不应为空：{body}"

    @pytest.mark.regression
    def test_withdraw_response_has_txn_id(self, withdraw_api):
        """TC-WITHDRAW-002 响应包含非空 txnId
        预期结果：data.txnId 为 POT 开头的字符串
        """
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            verified_data=VERIFIED_DATA,
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        data = assert_success(resp).get("data", {})
        print(f"\n[TC-WITHDRAW-002] data={data}")
        assert data.get("txnId"), f"txnId 不应为空：{data}"
        assert data["txnId"].startswith("POT"), f"txnId 应以 POT 开头：{data['txnId']}"

    @pytest.mark.regression
    def test_withdraw_initial_status_is_processing(self, withdraw_api):
        """TC-WITHDRAW-003 提款创建后状态为 PROCESSING
        预期结果：data.status = PROCESSING
        """
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            verified_data=VERIFIED_DATA,
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        data = assert_success(resp).get("data", {})
        print(f"\n[TC-WITHDRAW-003] status={data.get('status')}")
        assert data.get("status") == "PROCESSING", \
            f"初始状态应为 PROCESSING，实际：{data.get('status')}"

    @pytest.mark.regression
    def test_withdraw_account_id_in_response(self, withdraw_api):
        """TC-WITHDRAW-004 响应中 accountId 与请求 header 一致
        预期结果：data.accountId = WITHDRAW_ACCOUNT_ID
        """
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            verified_data=VERIFIED_DATA,
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        data = assert_success(resp).get("data", {})
        assert data.get("accountId") == WITHDRAW_ACCOUNT_ID, \
            f"accountId 应为 {WITHDRAW_ACCOUNT_ID}，实际：{data.get('accountId')}"

    @pytest.mark.regression
    def test_withdraw_request_id_echoed_back(self, withdraw_api):
        """TC-WITHDRAW-005 响应中 requestId 与请求一致（幂等标识回显）
        预期结果：data.requestId = 请求中的 requestId
        """
        req_id = _req_id()
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=req_id,
            verified_data=VERIFIED_DATA,
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        data = assert_success(resp).get("data", {})
        assert data.get("requestId") == req_id, \
            f"requestId 应回显 {req_id}，实际：{data.get('requestId')}"

    @pytest.mark.regression
    def test_withdraw_money_fields_structure(self, withdraw_api):
        """TC-WITHDRAW-006 withdrawalMoney / payoutMoney / fee 结构完整
        预期结果：三个字段均包含 ccy 和 amount，且 ccy=USDT
        """
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            verified_data=VERIFIED_DATA,
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        data = assert_success(resp).get("data", {})
        for field in ("withdrawalMoney", "payoutMoney"):
            assert data.get(field, {}).get("ccy") == "USDT", \
                f"{field}.ccy 应为 USDT，实际：{data.get(field)}"
            assert data.get(field, {}).get("amount"), \
                f"{field}.amount 不应为空，实际：{data.get(field)}"
        fee = data.get("fee", {}).get("money", {})
        assert fee.get("ccy") == "USDT", f"fee.money.ccy 应为 USDT，实际：{fee}"
        assert fee.get("amount"), f"fee.money.amount 不应为空，实际：{fee}"

    @pytest.mark.regression
    def test_withdraw_withdrawal_amount_matches_request(self, withdraw_api):
        """TC-WITHDRAW-007 withdrawalMoney.amount 与请求金额一致
        预期结果：withdrawalMoney.amount 等于请求的 amount（含小数位格式化）
        """
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            verified_data=VERIFIED_DATA,
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        data = assert_success(resp).get("data", {})
        actual_amount = data.get("withdrawalMoney", {}).get("amount", "")
        assert float(actual_amount) == float(VALID_AMOUNT), \
            f"withdrawalMoney.amount 应等于 {VALID_AMOUNT}，实际：{actual_amount}"

    @pytest.mark.regression
    def test_withdraw_bene_destination_address_not_empty(self, withdraw_api):
        """TC-WITHDRAW-008 响应中 bene.destinationAddress 不为空
        预期结果：bene.destinationAddress 为有效地址字符串
        """
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            verified_data=VERIFIED_DATA,
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        data = assert_success(resp).get("data", {})
        dest = data.get("bene", {}).get("destinationAddress", "")
        assert dest, f"bene.destinationAddress 不应为空：{data.get('bene')}"

    @pytest.mark.regression
    def test_withdraw_created_at_is_timestamp(self, withdraw_api):
        """TC-WITHDRAW-009 createdAt 为合理的毫秒时间戳
        预期结果：createdAt > 0，且为 13 位数字
        """
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            verified_data=VERIFIED_DATA,
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        data = assert_success(resp).get("data", {})
        created_at = data.get("createdAt", 0)
        assert isinstance(created_at, int) and created_at > 0, \
            f"createdAt 应为正整数时间戳，实际：{created_at}"
        assert len(str(created_at)) == 13, \
            f"createdAt 应为 13 位毫秒时间戳，实际：{created_at}"

    @pytest.mark.regression
    def test_withdraw_without_verified_data(self, withdraw_api):
        """TC-WITHDRAW-010 不传 verifiedData，接口正常处理
        预期结果：HTTP 200 或业务错误（非 5xx）
        """
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        print(f"\n[TC-WITHDRAW-010] {resp.status_code} {resp.json()}")
        assert resp.status_code < 500, f"不应返回 5xx，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_withdraw_idempotency_same_txn_id(self, withdraw_api):
        """TC-WITHDRAW-011 相同 requestId 重复提交，返回同一 txnId（幂等）
        步骤：用同一 requestId 调两次
        预期结果：两次 data.txnId 相同
        """
        req_id = _req_id()
        resp1 = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=req_id,
            verified_data=VERIFIED_DATA,
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        resp2 = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=req_id,
            verified_data=VERIFIED_DATA,
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        data1 = assert_success(resp1).get("data", {})
        data2 = assert_success(resp2).get("data", {})
        print(f"\n[TC-WITHDRAW-011] txnId1={data1.get('txnId')} txnId2={data2.get('txnId')}")
        assert data1.get("txnId") == data2.get("txnId"), \
            f"幂等调用应返回相同 txnId：{data1.get('txnId')} vs {data2.get('txnId')}"

    @pytest.mark.regression
    def test_withdraw_response_time(self, withdraw_api):
        """TC-WITHDRAW-012 接口响应时间应在 3000ms 以内"""
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            verified_data=VERIFIED_DATA,
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        assert_success(resp)
        assert_response_time(resp, max_ms=3000)


class TestWithdrawCryptoAbnormal:
    """异常场景"""

    @pytest.mark.regression
    def test_withdraw_amount_below_minimum(self, withdraw_api):
        """TC-WITHDRAW-101 amount 低于系统最小提款金额，返回 400
        预期结果：code=payment_schema_024，msg 含 amount less than min
        """
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount="0.000001",
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            verified_data=VERIFIED_DATA,
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        print(f"\n[TC-WITHDRAW-101] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"低于最小金额应返回 400，实际：{resp.status_code}"
        assert resp.json().get("code") == "payment_schema_024", \
            f"code 应为 payment_schema_024，实际：{resp.json()}"

    @pytest.mark.regression
    def test_withdraw_amount_zero(self, withdraw_api):
        """TC-WITHDRAW-102 amount=0，返回 400"""
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount="0",
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        print(f"\n[TC-WITHDRAW-102] {resp.status_code} {resp.json()}")
        assert resp.status_code in [400, 422], \
            f"amount=0 应返回 4xx，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_withdraw_negative_amount(self, withdraw_api):
        """TC-WITHDRAW-103 amount 为负数，返回 400"""
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount="-1",
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        print(f"\n[TC-WITHDRAW-103] {resp.status_code} {resp.json()}")
        assert resp.status_code in [400, 422], \
            f"负数 amount 应返回 4xx，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_withdraw_non_numeric_amount(self, withdraw_api):
        """TC-WITHDRAW-104 amount 为非数字字符串，返回 400"""
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount="abc",
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        print(f"\n[TC-WITHDRAW-104] {resp.status_code} {resp.json()}")
        assert resp.status_code in [400, 422], \
            f"非数字 amount 应返回 4xx，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_withdraw_insufficient_balance(self, withdraw_api):
        """TC-WITHDRAW-105 提款金额超过账户余额，返回余额不足错误
        预期结果：HTTP 400，code=000026，msg=Insufficient Balance
        """
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount="9999999",
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            verified_data=VERIFIED_DATA,
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        print(f"\n[TC-WITHDRAW-105] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"余额不足应返回 400，实际：{resp.status_code}"
        assert resp.json().get("code") == "000026", \
            f"code 应为 000026，实际：{resp.json()}"

    @pytest.mark.regression
    def test_withdraw_nonexistent_bene_id(self, withdraw_api):
        """TC-WITHDRAW-106 beneId 不存在，返回 400/404"""
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id="CBENE0000000000000000000",
            chain="ETHEREUM",
            request_id=_req_id(),
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        print(f"\n[TC-WITHDRAW-106] {resp.status_code} {resp.json()}")
        assert resp.status_code in [400, 404], \
            f"不存在的 beneId 应返回 4xx，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_withdraw_bene_id_belongs_to_other_account(self, withdraw_api):
        """TC-WITHDRAW-107 beneId 属于其他账户，返回 4xx
        预期结果：HTTP 400，code=000013（地址不在白名单）
        """
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=OTHER_ACCOUNT_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        print(f"\n[TC-WITHDRAW-107] {resp.status_code} {resp.json()}")
        assert resp.status_code in [400, 403], \
            f"跨账户 beneId 应返回 4xx，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_withdraw_missing_bene_id(self, withdraw_api):
        """TC-WITHDRAW-108 缺少 beneId 字段，返回 400"""
        resp = withdraw_api.post(
            "/v1/withdraw/crypto",
            headers={"X-ON-BEHALF-OF": WITHDRAW_ACCOUNT_ID},
            json={"ccy": "USDT", "amount": VALID_AMOUNT,
                  "chain": "ETHEREUM", "requestId": _req_id()},
        )
        print(f"\n[TC-WITHDRAW-108] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"缺少 beneId 应返回 400，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_withdraw_missing_ccy(self, withdraw_api):
        """TC-WITHDRAW-109 缺少 ccy 字段，返回 400"""
        resp = withdraw_api.post(
            "/v1/withdraw/crypto",
            headers={"X-ON-BEHALF-OF": WITHDRAW_ACCOUNT_ID},
            json={"amount": VALID_AMOUNT, "beneId": VALID_BENE_ID,
                  "chain": "ETHEREUM", "requestId": _req_id()},
        )
        print(f"\n[TC-WITHDRAW-109] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"缺少 ccy 应返回 400，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_withdraw_missing_amount(self, withdraw_api):
        """TC-WITHDRAW-110 缺少 amount 字段，返回 400"""
        resp = withdraw_api.post(
            "/v1/withdraw/crypto",
            headers={"X-ON-BEHALF-OF": WITHDRAW_ACCOUNT_ID},
            json={"ccy": "USDT", "beneId": VALID_BENE_ID,
                  "chain": "ETHEREUM", "requestId": _req_id()},
        )
        print(f"\n[TC-WITHDRAW-110] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"缺少 amount 应返回 400，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_withdraw_missing_chain(self, withdraw_api):
        """TC-WITHDRAW-111 缺少 chain 字段，返回 400"""
        resp = withdraw_api.post(
            "/v1/withdraw/crypto",
            headers={"X-ON-BEHALF-OF": WITHDRAW_ACCOUNT_ID},
            json={"ccy": "USDT", "amount": VALID_AMOUNT,
                  "beneId": VALID_BENE_ID, "requestId": _req_id()},
        )
        print(f"\n[TC-WITHDRAW-111] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"缺少 chain 应返回 400，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_withdraw_missing_request_id(self, withdraw_api):
        """TC-WITHDRAW-112 缺少 requestId 字段，返回 400"""
        resp = withdraw_api.post(
            "/v1/withdraw/crypto",
            headers={"X-ON-BEHALF-OF": WITHDRAW_ACCOUNT_ID},
            json={"ccy": "USDT", "amount": VALID_AMOUNT,
                  "beneId": VALID_BENE_ID, "chain": "ETHEREUM"},
        )
        print(f"\n[TC-WITHDRAW-112] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"缺少 requestId 应返回 400，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_withdraw_invalid_chain(self, withdraw_api):
        """TC-WITHDRAW-113 传入不支持的 chain，返回 400"""
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="INVALID_CHAIN",
            request_id=_req_id(),
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        print(f"\n[TC-WITHDRAW-113] {resp.status_code} {resp.json()}")
        assert resp.status_code in [400, 422], \
            f"无效 chain 应返回 4xx，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_withdraw_unsupported_ccy(self, withdraw_api):
        """TC-WITHDRAW-114 传入不支持的币种，返回 400"""
        resp = withdraw_api.withdraw_crypto(
            ccy="XYZ",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        print(f"\n[TC-WITHDRAW-114] {resp.status_code} {resp.json()}")
        assert resp.status_code in [400, 422], \
            f"不支持的币种应返回 4xx，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_withdraw_without_account_header(self, withdraw_api):
        """TC-WITHDRAW-115 不传 X-ON-BEHALF-OF header，返回 4xx
        预期结果：HTTP 400/401/403（主账户没有加密钱包或不允许直接提款）
        """
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
        )
        print(f"\n[TC-WITHDRAW-115] {resp.status_code} {resp.json()}")
        assert resp.status_code < 500, \
            f"不传 header 不应返回 5xx，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_withdraw_invalid_account_id_format(self, withdraw_api):
        """TC-WITHDRAW-116 X-ON-BEHALF-OF 传入非 ACC 格式，返回 4xx"""
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            account_id="invalid_id_001",
        )
        print(f"\n[TC-WITHDRAW-116] {resp.status_code} {resp.json()}")
        assert resp.status_code in [400, 401, 403], \
            f"非法格式 accountId 应返回 4xx，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_withdraw_nonexistent_account_id(self, withdraw_api):
        """TC-WITHDRAW-117 X-ON-BEHALF-OF 传入不存在的账户，返回 4xx
        预期结果：HTTP 403/404，code=000029（Connect accountId not exist）
        """
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="ETHEREUM",
            request_id=_req_id(),
            account_id="ACC0000000000000000000",
        )
        print(f"\n[TC-WITHDRAW-117] {resp.status_code} {resp.json()}")
        assert resp.status_code in [400, 403, 404], \
            f"不存在账户应返回 4xx，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_withdraw_ccy_chain_mismatch(self, withdraw_api):
        """TC-WITHDRAW-118 ccy 与 chain 不匹配（如 USDT + 不支持该链），返回 400
        预期结果：HTTP 400，提示链不支持该币种
        """
        resp = withdraw_api.withdraw_crypto(
            ccy="USDT",
            amount=VALID_AMOUNT,
            bene_id=VALID_BENE_ID,
            chain="BITCOIN",
            request_id=_req_id(),
            account_id=WITHDRAW_ACCOUNT_ID,
        )
        print(f"\n[TC-WITHDRAW-118] {resp.status_code} {resp.json()}")
        assert resp.status_code in [400, 422], \
            f"ccy/chain 不匹配应返回 4xx，实际：{resp.status_code}"
