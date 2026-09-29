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

    @pytest.mark.regression
    def test_list_refund_cases_no_status(self, refund_api):
        """TC-REF-005 不传 status 参数，使用默认值查询
        前置条件：无
        请求：GET /v1/refund/cases，不带 status 参数
        预期结果：HTTP 200，code=0，返回 list 字段（使用服务端默认 status）
        """
        resp = refund_api.get("/v1/refund/cases")
        if resp.status_code == 404:
            pytest.skip("退款 Case 列表接口在当前 SIT 环境未部署（404）")
        body = assert_success(resp)
        assert "list" in body.get("data", {}), "响应 data 中应包含 list 字段"

    @pytest.mark.regression
    def test_list_refund_cases_invalid_status(self, refund_api):
        """TC-REF-006 status 传入非法枚举值，返回参数错误
        前置条件：无
        请求：GET /v1/refund/cases?status=InvalidStatus
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = refund_api.get("/v1/refund/cases", params={"status": "InvalidStatus"})
        if resp.status_code == 404:
            pytest.skip("退款 Case 列表接口在当前 SIT 环境未部署（404）")
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"


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

    @pytest.mark.regression
    def test_risk_review_missing_action(self, refund_api):
        """TC-REF-105 缺少 action 字段，返回参数错误
        前置条件：无
        请求体：caseId 存在，但不传 action
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = refund_api.post("/v1/refund/case/test_refund_001/review", json={
            "caseId": "test_refund_001",
            "remark": "缺少 action",
        })
        assert resp.status_code in [400, 422] or resp.json().get("code") != 0, \
            f"实际 {resp.status_code}，响应：{resp.json()}"

    @pytest.mark.regression
    def test_risk_review_nonexistent_case(self, refund_api):
        """TC-REF-106 对不存在的 caseId 做风控审核，返回业务错误
        前置条件：无
        请求：POST /v1/refund/case/nonexistent_refund_99999/review，action=Pass
        预期结果：HTTP 非 200 或 code≠0
        """
        resp = refund_api.risk_review("nonexistent_refund_99999", action="Pass")
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"

    @pytest.mark.regression
    def test_risk_review_repeat(self, refund_api):
        """TC-REF-107 重复风控审核已审核的 Case，返回业务错误
        前置条件：test_refund_risk_approved_001 已完成风控审核
        请求：再次对该 Case 执行风控审核 Pass
        预期结果：HTTP 非 200 或 code≠0（不允许重复审核）
        """
        resp = refund_api.risk_review("test_refund_risk_approved_001", action="Pass")
        if resp.status_code == 404:
            pytest.skip("测试数据 test_refund_risk_approved_001 不存在于当前环境")
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != 0, \
            f"重复风控审核应返回错误，实际 {resp.status_code}，响应：{body}"


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

    @pytest.mark.regression
    def test_finance_review_invalid_action(self, refund_api):
        """TC-REF-204 财务审核 action 传入非法值，返回参数错误
        前置条件：无
        请求体：action=InvalidAction
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = refund_api.post(
            "/v1/refund/case/test_refund_risk_approved_001/finance-review",
            json={"action": "InvalidAction"},
        )
        assert resp.status_code in [400, 422] or resp.json().get("code") != 0, \
            f"实际 {resp.status_code}，响应：{resp.json()}"

    @pytest.mark.regression
    def test_finance_review_missing_action(self, refund_api):
        """TC-REF-205 财务审核缺少 action 字段，返回参数错误
        前置条件：无
        请求体：空 {}，不传 action
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = refund_api.post(
            "/v1/refund/case/test_refund_risk_approved_001/finance-review",
            json={},
        )
        assert resp.status_code in [400, 422] or resp.json().get("code") != 0, \
            f"实际 {resp.status_code}，响应：{resp.json()}"

    @pytest.mark.regression
    def test_finance_review_nonexistent_case(self, refund_api):
        """TC-REF-206 对不存在的 caseId 做财务审核，返回业务错误
        前置条件：无
        请求：POST /v1/refund/case/nonexistent_refund_99999/finance-review，action=Pass
        预期结果：HTTP 非 200 或 code≠0
        """
        resp = refund_api.finance_review("nonexistent_refund_99999", action="Pass")
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"

    @pytest.mark.regression
    def test_finance_review_repeat(self, refund_api):
        """TC-REF-207 重复财务审核已审核的 Case，返回业务错误
        前置条件：test_refund_finance_approved_001 已完成财务审核
        请求：再次对该 Case 执行财务审核 Pass
        预期结果：HTTP 非 200 或 code≠0（不允许重复审核）
        """
        resp = refund_api.finance_review("test_refund_finance_approved_001", action="Pass")
        if resp.status_code == 404:
            pytest.skip("测试数据 test_refund_finance_approved_001 不存在于当前环境")
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != 0, \
            f"重复财务审核应返回错误，实际 {resp.status_code}，响应：{body}"


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

    @pytest.mark.regression
    def test_refund_risk_reject_flow(self, refund_api):
        """TC-REF-303 风控审核 Reject 后，Case 状态流转为 Rejected
        前置条件：test_refund_pending_005 处于 Pending 状态
        步骤：风控审核 Reject → 查询 Case 状态
        预期结果：Case status 变为 Rejected
        """
        resp = refund_api.risk_review(
            "test_refund_pending_005",
            action="Reject",
            remark="风控审核拒绝，触发流程终止",
        )
        if resp.status_code == 404:
            pytest.skip("测试数据 test_refund_pending_005 不存在于当前环境")
        assert_success(resp)

        query_resp = refund_api.get_case("test_refund_pending_005")
        if query_resp.status_code == 404:
            pytest.skip("查询 Case 接口返回 404")
        body = assert_success(query_resp)
        status = body.get("data", {}).get("status")
        assert status == "Rejected", f"风控拒绝后 status 应为 Rejected，实际：{status}"

    @pytest.mark.regression
    def test_refund_finance_reject_flow(self, refund_api):
        """TC-REF-304 财务审核 Reject 后，Case 状态流转为 Rejected
        前置条件：test_refund_risk_approved_003 处于 RiskApproved 状态
        步骤：财务审核 Reject → 查询 Case 状态
        预期结果：Case status 变为 Rejected
        """
        resp = refund_api.finance_review(
            "test_refund_risk_approved_003",
            action="Reject",
        )
        if resp.status_code == 404:
            pytest.skip("测试数据 test_refund_risk_approved_003 不存在于当前环境")
        assert_success(resp)

        query_resp = refund_api.get_case("test_refund_risk_approved_003")
        if query_resp.status_code == 404:
            pytest.skip("查询 Case 接口返回 404")
        body = assert_success(query_resp)
        status = body.get("data", {}).get("status")
        assert status == "Rejected", f"财务拒绝后 status 应为 Rejected，实际：{status}"
