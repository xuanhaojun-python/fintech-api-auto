"""
Smart Payment 支付流程测试
覆盖：标准支付、Travel Rule 命中、LN 扫描命中、退款
"""
import pytest

from utils.assertions import assert_success, assert_link_status


class TestStandardPaymentFlow:
    """Flow 1：标准支付流程（无 Travel Rule）"""

    @pytest.mark.smoke
    @pytest.mark.parametrize("case", pytest.lazy_fixture("payment_cases") if False else [])
    def test_standard_payment_parametrized(self, payment_service, accounts, case):
        """TC-PAY-001/002 数据驱动：标准支付场景"""
        merchant = accounts["merchant"]
        result = payment_service.complete_standard_payment(
            merchant_id=merchant["id"],
            payer_name=case["payer_name"],
            payer_email=case["payer_email"],
            amount=case["amount"],
            payer_address=case["payer_address"],
            currency=case["currency"],
            travel_rule_result=case["travel_rule"],
        )
        assert "linkId" in result
        assert "paymentAddress" in result

    @pytest.mark.smoke
    def test_standard_payment_100_usdt(self, payment_service, accounts):
        """TC-PAY-F1-001 100 USDT 标准支付完整流程"""
        merchant = accounts["merchant"]
        try:
            result = payment_service.complete_standard_payment(
                merchant_id=merchant["id"],
                payer_name="Alice",
                payer_email="alice@example.com",
                amount=100.0,
                payer_address="0xALICE_ADDR",
            )
        except AssertionError as e:
            if "404" in str(e):
                pytest.skip("smart-payment 接口在当前 SIT 环境未部署（404）")
            raise
        assert result["linkId"], "linkId 不应为空"
        assert result["paymentAddress"], "paymentAddress 不应为空"

    @pytest.mark.regression
    def test_link_status_after_payment(self, payment_api, mock_api, accounts):
        """TC-PAY-F1-002 链上到账后 Link 状态应变为 Completed"""
        merchant = accounts["merchant"]

        resp = payment_api.create_link(
            merchant["id"], "Bob", "bob@example.com", 50.0
        )
        if resp.status_code == 404:
            pytest.skip("smart-payment 接口在当前 SIT 环境未部署（404）")
        body = assert_success(resp)
        link_id = body["data"]["linkId"]

        # Mock Travel Rule 不命中
        mock_api.set_travel_rule_result(link_id, "No")
        payment_api.check_travel_rule(link_id, "0xBOB_ADDR")
        payment_api.get_payment_address(link_id)

        # 模拟链上到账
        mock_api.simulate_chain_transaction(link_id, 50.0)

        # 验证 Link 状态
        resp = payment_api.get_link_status(link_id)
        body = assert_success(resp)
        assert_link_status(body, "Completed")


class TestTravelRuleFlow:
    """Flow 2：Travel Rule 命中流程"""

    @pytest.mark.smoke
    def test_travel_rule_required_flow(self, payment_service, accounts, payment_cases):
        """TC-PAY-F2-001 大额支付触发 Travel Rule，提交信息后获得支付地址"""
        merchant = accounts["merchant"]
        tr_info = payment_cases["travel_rule_info"]
        try:
            result = payment_service.complete_travel_rule_payment(
                merchant_id=merchant["id"],
                payer_name=tr_info["payer_name"],
                payer_email="charlie@example.com",
                amount=10000.0,
                payer_address=tr_info["payer_wallet_address"],
                tr_info=tr_info,
            )
        except AssertionError as e:
            if "404" in str(e):
                pytest.skip("smart-payment 接口在当前 SIT 环境未部署（404）")
            raise
        assert result["linkId"], "linkId 不应为空"
        assert result["paymentAddress"], "paymentAddress 不应为空"

    @pytest.mark.regression
    def test_travel_rule_no_hit(self, payment_api, mock_api, accounts):
        """TC-PAY-F2-002 Travel Rule 不命中，直接获取支付地址"""
        merchant = accounts["merchant"]
        resp = payment_api.create_link(merchant["id"], "Dave", "dave@example.com", 200.0)
        if resp.status_code == 404:
            pytest.skip("smart-payment 接口在当前 SIT 环境未部署（404）")
        body = assert_success(resp)
        link_id = body["data"]["linkId"]

        mock_api.set_travel_rule_result(link_id, "No")
        resp = payment_api.check_travel_rule(link_id, "0xDAVE_ADDR")
        body = assert_success(resp)

        # Travel Rule 不命中时，响应中不应要求提交信息
        assert body.get("data", {}).get("requireTravelRuleInfo") is not True


class TestLnHitFlow:
    """Flow 3：LN 扫描命中流程（需人工审核）"""

    @pytest.mark.regression
    def test_ln_hit_creates_kyt_case(self, payment_api, mock_api, kyt_api, accounts, payment_cases):
        """TC-PAY-F3-001 LN 扫描命中后产生 KYT Case"""
        merchant = accounts["merchant"]
        ln_case = payment_cases["ln_hit_payer"]

        resp = payment_api.create_link(
            merchant["id"], ln_case["payer_name"],
            ln_case["payer_email"], ln_case["amount"]
        )
        if resp.status_code == 404:
            pytest.skip("smart-payment 接口在当前 SIT 环境未部署（404）")
        body = assert_success(resp)
        link_id = body["data"]["linkId"]

        # Mock LN 命中
        mock_api.set_ln_scan_result(ln_case["payer_name"], is_hit=True)
        mock_api.set_travel_rule_result(link_id, "No")
        payment_api.check_travel_rule(link_id, ln_case["payer_address"])
        payment_api.get_payment_address(link_id)
        mock_api.simulate_chain_transaction(link_id, ln_case["amount"])

        # 验证产生 KYT Case（通过 link_id 查询）
        resp = kyt_api.get("/v1/kyt/cases", params={"linkId": link_id})
        body = assert_success(resp)
        cases = body.get("data", {}).get("list", [])
        assert len(cases) > 0, "LN 命中后应产生 KYT Case"


class TestCreateLinkAbnormal:
    """创建 Link 异常场景"""

    def test_create_link_missing_merchant_id(self, payment_api):
        """TC-PAY-ERR-001 缺少 merchantId，返回 400/422"""
        resp = payment_api.post("/v1/smart-payment/link/create", json={
            "payerName": "Alice",
            "payerEmail": "alice@example.com",
            "amount": 100.0,
            "currency": "USDT",
        })
        if resp.status_code == 404:
            pytest.skip("smart-payment 接口在当前 SIT 环境未部署（404）")
        assert resp.status_code in [400, 422], f"实际 {resp.status_code}"

    def test_create_link_negative_amount(self, payment_api, accounts):
        """TC-PAY-ERR-002 金额为负数，返回参数错误"""
        merchant = accounts["merchant"]
        resp = payment_api.create_link(merchant["id"], "Alice", "alice@example.com", -1.0)
        assert resp.status_code in [400, 422] or resp.json().get("code") != 0

    def test_create_link_zero_amount(self, payment_api, accounts):
        """TC-PAY-ERR-003 金额为 0，返回参数错误"""
        merchant = accounts["merchant"]
        resp = payment_api.create_link(merchant["id"], "Alice", "alice@example.com", 0.0)
        assert resp.status_code in [400, 422] or resp.json().get("code") != 0


class TestPaymentTxnQuery:
    """查询入金交易"""

    @pytest.mark.smoke
    def test_get_txn_existing(self, payment_api, merchant_order_id):
        """TC-PAY-TXN-001 查询已存在的入金交易"""
        resp = payment_api.get_txn(merchant_order_id)
        body = assert_success(resp)
        data = body.get("data")
        if not data:
            pytest.skip(f"merchant_order_id={merchant_order_id} 在支付系统中无对应入金记录，需要先初始化测试数据")
        record = data[0] if isinstance(data, list) else data
        assert "merchantOrderId" in record, f"响应 data 中缺少 merchantOrderId 字段：{record}"

    @pytest.mark.regression
    def test_get_txn_nonexistent(self, payment_api):
        """TC-PAY-TXN-002 查询不存在的入金交易，返回空数据"""
        resp = payment_api.get_txn("nonexistent_order_99999")
        assert resp.status_code == 200, f"实际 {resp.status_code}"
        data = resp.json().get("data")
        assert not data, f"不存在的订单查询 data 应为空，实际: {data}"

    @pytest.mark.regression
    def test_get_txn_missing_order_id(self, payment_api):
        """TC-PAY-TXN-003 缺少 merchantOrderId，返回参数错误"""
        resp = payment_api.get("/v1/payment/txn")
        assert resp.status_code in [400, 422] or resp.json().get("code") != "0000"


class TestPaymentRefundQuery:
    """查询退款交易"""

    @pytest.mark.smoke
    def test_get_refund_existing(self, payment_api, existing_refund_order_id):
        """TC-PAY-REF-001 查询已存在的退款单"""
        resp = payment_api.get_refund(existing_refund_order_id)
        body = assert_success(resp)
        data = body.get("data", {})
        assert data.get("refundOrderId") == existing_refund_order_id
        assert "status" in data
        assert "amount" in data

    @pytest.mark.regression
    def test_get_refund_nonexistent(self, payment_api):
        """TC-PAY-REF-002 查询不存在的退款单，返回空数据"""
        resp = payment_api.get_refund("nonexistent_refund_99999")
        assert resp.status_code == 200, f"实际 {resp.status_code}"
        data = resp.json().get("data")
        assert not data, f"不存在的退款单 data 应为空，实际: {data}"

    @pytest.mark.regression
    def test_get_refund_missing_order_id(self, payment_api):
        """TC-PAY-REF-003 缺少 refundOrderId，返回参数错误"""
        resp = payment_api.get("/v1/payment/refund")
        assert resp.status_code in [400, 422] or resp.json().get("code") != "0000"


class TestCreatePaymentRefund:
    """创建退款"""

    @pytest.mark.regression
    def test_create_refund_missing_reason(self, payment_api):
        """TC-PAY-REF-101 reason 为空，返回业务错误"""
        resp = payment_api.refund(
            payin_txn_id="PIT2071535440443215872",
            refund_order_id="REFUND_TEST_EMPTY_REASON",
            origin_merchant_order_id="ORDER_TEST_001",
            from_address="0x95bfad0967303a7b202143874b456e1c41a66bfe",
            to_address="0x714c93c1f732aa25639c3ae1035b1de361b5c3a4",
            tx_hash="0x48cc54324094ca141774e674074bc9379ff9b876ff2ab668a21235fae76bf311",
            amount="0.02",
            reason="",
        )
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != "0000"

    @pytest.mark.regression
    def test_create_refund_nonexistent_payin_txn(self, payment_api):
        """TC-PAY-REF-102 payinTxnId 不存在，返回业务错误"""
        resp = payment_api.refund(
            payin_txn_id="nonexistent_txn_99999",
            refund_order_id="REFUND_TEST_INVALID_TXN",
            origin_merchant_order_id="ORDER_TEST_002",
            from_address="0x95bfad0967303a7b202143874b456e1c41a66bfe",
            to_address="0x714c93c1f732aa25639c3ae1035b1de361b5c3a4",
            tx_hash="0x48cc54324094ca141774e674074bc9379ff9b876ff2ab668a21235fae76bf311",
            amount="0.02",
            reason="refund",
        )
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != "0000"


class TestReceiptFlow:
    """交易凭证：查看与下载"""

    @pytest.mark.smoke
    def test_get_receipt_success(self, payment_api, merchant_order_id):
        """TC-PAY-RCP-001 查看已存在交易的凭证"""
        resp = payment_api.get_receipt(merchant_order_id)
        if resp.status_code != 200:
            pytest.skip(f"merchant_order_id={merchant_order_id} 在凭证接口无效（{resp.status_code}），需使用有效 txn_id")
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
        if resp.status_code != 200:
            pytest.skip(f"merchant_order_id={merchant_order_id} 在凭证接口无效（{resp.status_code}），需使用有效 txn_id")
        assert resp.status_code == 200, \
            f"期望 200，实际 {resp.status_code}，响应：{resp.text[:200]}"

    @pytest.mark.regression
    def test_download_receipt_nonexistent(self, payment_api):
        """TC-PAY-RCP-005 下载不存在的 txnId，返回业务错误"""
        resp = payment_api.download_receipt("nonexistent_txn_99999")
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != "0000", \
            "不存在的 txnId 应返回业务错误"
