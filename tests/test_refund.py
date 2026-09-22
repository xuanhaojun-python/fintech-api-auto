"""
退款流程接口测试
覆盖：查询退款 Case、风控审核、财务审核、完整退款流程
"""
import pytest

from utils.assertions import assert_success, assert_field


class TestRefundCaseQuery:
    """退款 Case 查询"""

    @pytest.mark.smoke
    def test_list_pending_refund_cases(self, refund_api):
        """TC-REF-001 查询 Pending 状态退款 Case 列表"""
        resp = refund_api.list_cases(status="Pending")
        if resp.status_code == 404:
            pytest.skip("退款 Case 列表接口在当前 SIT 环境未部署（404）")
        body = assert_success(resp)
        assert_field(body, "data", "list")

    @pytest.mark.regression
    def test_list_refund_cases_by_status(self, refund_api):
        """TC-REF-002 按各状态查询退款 Case 列表"""
        for status in ["Pending", "RiskApproved", "FinanceApproved", "Completed", "Rejected"]:
            resp = refund_api.list_cases(status=status)
            if resp.status_code == 404:
                pytest.skip("退款 Case 列表接口在当前 SIT 环境未部署（404）")
            body = assert_success(resp)
            assert "list" in body.get("data", {}), f"status={status} 时响应缺少 list 字段"

    def test_get_refund_case_detail(self, refund_api):
        """TC-REF-003 查询单个退款 Case 详情"""
        resp = refund_api.get_case("test_refund_case_001")
        if resp.status_code == 404:
            pytest.skip("测试数据 test_refund_case_001 不存在于当前环境")
        body = assert_success(resp)
        assert_field(body, "data", "caseId")
        assert_field(body, "data", "status")
        assert_field(body, "data", "amount")

    def test_get_nonexistent_refund_case(self, refund_api):
        """TC-REF-004 查询不存在的退款 Case，返回业务错误"""
        resp = refund_api.get_case("nonexistent_refund_99999")
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != 0


class TestRiskReview:
    """风控审核"""

    @pytest.mark.smoke
    def test_risk_review_pass(self, refund_api):
        """TC-REF-101 风控审核 Pass"""
        resp = refund_api.risk_review("test_refund_pending_001", action="Pass")
        if resp.status_code == 404:
            pytest.skip("测试数据 test_refund_pending_001 不存在于当前环境")
        assert_success(resp)

    @pytest.mark.regression
    def test_risk_review_pass_with_final_amount(self, refund_api):
        """TC-REF-102 风控审核 Pass，调整最终退款金额"""
        resp = refund_api.risk_review(
            "test_refund_pending_002",
            action="Pass",
            final_amount=90.0,
            remark="扣除手续费后实际退款 90 USDT",
        )
        if resp.status_code == 404:
            pytest.skip("测试数据 test_refund_pending_002 不存在于当前环境")
        body = assert_success(resp)
        final = body.get("data", {}).get("finalRefundAmount")
        assert final == 90.0, f"期望最终金额 90.0，实际 {final}"

    @pytest.mark.regression
    def test_risk_review_reject(self, refund_api):
        """TC-REF-103 风控审核 Reject"""
        resp = refund_api.risk_review(
            "test_refund_pending_003",
            action="Reject",
            remark="地址验证失败，拒绝退款",
        )
        if resp.status_code == 404:
            pytest.skip("测试数据 test_refund_pending_003 不存在于当前环境")
        assert_success(resp)

    def test_risk_review_invalid_action(self, refund_api):
        """TC-REF-104 无效的 action 值，返回参数错误"""
        resp = refund_api.post("/v1/refund/case/test_refund_001/review", json={
            "caseId": "test_refund_001",
            "action": "InvalidAction",
        })
        assert resp.status_code in [400, 422] or resp.json().get("code") != 0


class TestFinanceReview:
    """财务审核"""

    @pytest.mark.smoke
    def test_finance_review_pass(self, refund_api):
        """TC-REF-201 财务审核 Pass"""
        resp = refund_api.finance_review("test_refund_risk_approved_001", action="Pass")
        if resp.status_code == 404:
            pytest.skip("测试数据 test_refund_risk_approved_001 不存在于当前环境")
        assert_success(resp)

    @pytest.mark.regression
    def test_finance_review_reject(self, refund_api):
        """TC-REF-202 财务审核 Reject"""
        resp = refund_api.finance_review(
            "test_refund_risk_approved_002", action="Reject"
        )
        if resp.status_code == 404:
            pytest.skip("测试数据 test_refund_risk_approved_002 不存在于当前环境")
        assert_success(resp)

    def test_finance_review_before_risk_review(self, refund_api):
        """TC-REF-203 跳过风控审核直接财务审核，应返回业务错误"""
        resp = refund_api.finance_review("test_refund_pending_004", action="Pass")
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != 0, "未经风控审核不应进入财务审核"


class TestCompleteRefundFlow:
    """完整退款流程（端到端）"""

    @pytest.mark.smoke
    def test_refund_now_full_flow(self, refund_service):
        """TC-REF-301 立即退款完整流程：KYT Reject → 风控 Pass → 财务 Pass"""
        try:
            result = refund_service.complete_refund_now(
                txn_id="test_txn_refund_flow_001",
                refund_address="0xREFUND_TARGET_ADDR",
            )
        except AssertionError as e:
            if "404" in str(e):
                pytest.skip("测试数据 test_txn_refund_flow_001 不存在或退款接口未部署（404）")
            raise
        assert result["kytCaseId"], "kytCaseId 不应为空"
        assert result["refundCaseId"], "refundCaseId 不应为空"

    @pytest.mark.regression
    def test_refund_later_full_flow(self, refund_service):
        """TC-REF-302 延迟退款完整流程：KYT Reject → 风控 Pass（含金额调整）→ 财务 Pass"""
        try:
            result = refund_service.complete_refund_later(
                txn_id="test_txn_refund_flow_002",
                final_amount=95.0,
                refund_address="0xREFUND_TARGET_ADDR_2",
            )
        except AssertionError as e:
            if "404" in str(e):
                pytest.skip("测试数据 test_txn_refund_flow_002 不存在或退款接口未部署（404）")
            raise
        assert result["kytCaseId"], "kytCaseId 不应为空"
        assert result["refundCaseId"], "refundCaseId 不应为空"
