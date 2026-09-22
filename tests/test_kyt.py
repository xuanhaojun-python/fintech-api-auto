"""
KYT 审核接口测试
覆盖：查询 Case、LN Case 排查、一审 Approve / Reject
"""
import pytest

from utils.assertions import assert_success, assert_field


class TestKytCaseQuery:
    """KYT Case 查询"""   

    @pytest.mark.smoke
    def test_get_existing_case(self, kyt_api):
        """TC-KYT-001 查询已存在的 KYT Case"""
        resp = kyt_api.get_case("test_txn_pending_001")
        if resp.status_code == 404:
            pytest.skip("测试数据 test_txn_pending_001 不存在于当前环境，需先完成数据初始化")
        body = assert_success(resp)
        assert_field(body, "data", "caseId")
        assert_field(body, "data", "status")

    def test_get_nonexistent_case(self, kyt_api):
        """TC-KYT-002 查询不存在的 Case，返回业务错误"""
        resp = kyt_api.get_case("nonexistent_txn_99999")
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != 0

    def test_get_ln_cases(self, kyt_api):
        """TC-KYT-003 查询 LN 扫描 Case 列表"""
        resp = kyt_api.get_case("test_txn_ln_hit_001")
        if resp.status_code == 404:
            pytest.skip("测试数据 test_txn_ln_hit_001 不存在于当前环境")
        body = assert_success(resp)
        kyt_case_id = body["data"]["caseId"]

        resp = kyt_api.get_ln_cases(kyt_case_id)
        body = assert_success(resp)
        ln_cases = body.get("data", {}).get("list", [])
        assert len(ln_cases) > 0, "LN 命中的 Case 应有 LN Case 列表"


class TestKytApprove:
    """KYT 一审 Approve"""

    @pytest.mark.smoke
    def test_approve_clean_transaction(self, kyt_api):
        """TC-KYT-101 正常交易 KYT 一审 Approve"""
        resp = kyt_api.get_case("test_txn_pending_001")
        if resp.status_code == 404:
            pytest.skip("测试数据 test_txn_pending_001 不存在于当前环境")
        body = assert_success(resp)
        kyt_case_id = body["data"]["caseId"]

        resp = kyt_api.approve(kyt_case_id)
        body = assert_success(resp)
        assert body.get("data", {}).get("status") in ["Approved", "Completed"]

    def test_approve_already_approved_case(self, kyt_api):
        """TC-KYT-102 重复 Approve 已审核 Case，返回业务错误"""
        resp = kyt_api.get_case("test_txn_approved_001")
        if resp.status_code == 404:
            pytest.skip("测试数据 test_txn_approved_001 不存在于当前环境")
        body = assert_success(resp)
        kyt_case_id = body["data"]["caseId"]

        resp = kyt_api.approve(kyt_case_id)
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != 0, "重复审核应返回错误"


class TestKytReject:
    """KYT 一审 Reject"""

    @pytest.mark.smoke
    def test_reject_refund_now(self, kyt_api):
        """TC-KYT-201 Reject + 立即退款"""
        resp = kyt_api.get_case("test_txn_pending_002")
        if resp.status_code == 404:
            pytest.skip("测试数据 test_txn_pending_002 不存在于当前环境")
        body = assert_success(resp)
        kyt_case_id = body["data"]["caseId"]

        resp = kyt_api.reject(
            kyt_case_id,
            reject_type=["Refund"],
            refund_result="RefundNow",
            refund_address="0xREFUND_ADDR",
        )
        assert_success(resp)

    @pytest.mark.regression
    def test_reject_refund_later(self, kyt_api):
        """TC-KYT-202 Reject + 延迟退款"""
        resp = kyt_api.get_case("test_txn_pending_003")
        if resp.status_code == 404:
            pytest.skip("测试数据 test_txn_pending_003 不存在于当前环境")
        body = assert_success(resp)
        kyt_case_id = body["data"]["caseId"]

        resp = kyt_api.reject(
            kyt_case_id,
            reject_type=["Refund"],
            refund_result="RefundLater",
            refund_address="0xREFUND_ADDR",
        )
        assert_success(resp)

    @pytest.mark.regression
    def test_reject_mark_polluted(self, kyt_api):
        """TC-KYT-203 Reject + 标记污染地址"""
        resp = kyt_api.get_case("test_txn_pending_004")
        if resp.status_code == 404:
            pytest.skip("测试数据 test_txn_pending_004 不存在于当前环境")
        body = assert_success(resp)
        kyt_case_id = body["data"]["caseId"]

        resp = kyt_api.reject(
            kyt_case_id,
            reject_type=["Polluted"],
            refund_result="NoRefund",
            mark_polluted=True,
            remark="已知污染地址",
        )
        assert_success(resp)

    def test_reject_missing_refund_result(self, kyt_api):
        """TC-KYT-204 Reject 缺少 refundResult，返回参数错误"""
        resp = kyt_api.post("/v1/kyt/case/test_case_001/reject", json={
            "caseId": "test_case_001",
            "rejectType": ["Refund"],
        })
        assert resp.status_code in [400, 422] or resp.json().get("code") != 0


class TestTravelRuleCollect:
    """Travel Rule 信息采集"""

    @pytest.mark.smoke
    def test_collect_travel_rule_info(self, kyt_api):
        """TC-KYT-401 正常采集 Travel Rule 信息"""
        resp = kyt_api.collect_travel_rule_info(
            merchant_order_id="xuanhaojun_uat_2026041606",
            txn_type="SMART_PAYMENT",
            legal_entity="PDCA",
            amount="2.26",
            ccy="USDT",
            protocol="ETHEREUM",
        )
        print(f"\n[TC-KYT-401] 响应状态码: {resp.status_code}")
        print(f"[TC-KYT-401] 响应体: {resp.json()}")
        assert_success(resp)

    @pytest.mark.regression
    def test_collect_travel_rule_missing_merchant_order_id(self, kyt_api):
        """TC-KYT-402 缺少 merchantOrderId，返回业务错误 9999"""
        resp = kyt_api.post("/v1/kyt/travel-rule/check", json={
            "txnType": "SMART_PAYMENT",
            "legalEntity": "PDCA",
            "amount": "2.26",
            "ccy": "USDT",
            "protocol": "ETHEREUM",
        })
        body = resp.json()
        assert body.get("code") == "9999"
        assert "merchant order id" in body.get("msg", "").lower()

    @pytest.mark.regression
    def test_collect_travel_rule_missing_amount(self, kyt_api):
        """TC-KYT-403 缺少 amount，返回业务错误 9999"""
        resp = kyt_api.post("/v1/kyt/travel-rule/check", json={
            "merchantOrderId": "xuanhaojun_uat_2026041606",
            "txnType": "SMART_PAYMENT",
            "legalEntity": "PDCA",
            "ccy": "USDT",
            "protocol": "ETHEREUM",
        })
        body = resp.json()
        assert body.get("code") == "9999"
        assert "amount" in body.get("msg", "").lower()


class TestLnCaseReview:
    """LN Case 人工排查"""

    @pytest.mark.regression
    def test_complete_ln_case_pass(self, kyt_api):
        """TC-KYT-301 LN Case 排查结果 Pass"""
        resp = kyt_api.get_case("test_txn_ln_hit_001")
        if resp.status_code == 404:
            pytest.skip("测试数据 test_txn_ln_hit_001 不存在于当前环境")
        body = assert_success(resp)
        kyt_case_id = body["data"]["caseId"]

        resp = kyt_api.get_ln_cases(kyt_case_id)
        body = assert_success(resp)
        ln_case_id = body["data"]["list"][0]["lnCaseId"]

        resp = kyt_api.complete_ln_case(ln_case_id, result="Pass", remark="人工核查无风险")
        assert_success(resp)

    @pytest.mark.regression
    def test_complete_ln_case_fail(self, kyt_api):
        """TC-KYT-302 LN Case 排查结果 Fail"""
        resp = kyt_api.get_case("test_txn_ln_hit_002")
        if resp.status_code == 404:
            pytest.skip("测试数据 test_txn_ln_hit_002 不存在于当前环境")
        body = assert_success(resp)
        kyt_case_id = body["data"]["caseId"]

        resp = kyt_api.get_ln_cases(kyt_case_id)
        body = assert_success(resp)
        ln_case_id = body["data"]["list"][0]["lnCaseId"]

        resp = kyt_api.complete_ln_case(ln_case_id, result="Fail", remark="确认制裁名单")
        assert_success(resp)
