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

    def test_get_ln_cases_nonexistent_case(self, kyt_api):
        """TC-KYT-004 对不存在的 caseId 查询 LN Case 列表，返回业务错误
        前置条件：无
        请求：/v1/kyt/case/nonexistent_case_99999/ln-cases
        预期结果：HTTP 非 200 或 code≠0
        """
        resp = kyt_api.get_ln_cases("nonexistent_case_99999")
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"

    def test_get_case_empty_txn_id(self, kyt_api):
        """TC-KYT-005 txnId 为空字符串，返回 404 或路由错误
        前置条件：无
        请求：GET /v1/kyt/case/（路径参数为空）
        预期结果：HTTP 400/404/405
        """
        resp = kyt_api.get("/v1/kyt/case/")
        assert resp.status_code in [400, 404, 405], \
            f"实际 {resp.status_code}，响应：{resp.text}"


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

    def test_approve_nonexistent_case(self, kyt_api):
        """TC-KYT-103 approve 不存在的 caseId，返回业务错误
        前置条件：无
        请求：POST /v1/kyt/case/nonexistent_case_99999/approve
        预期结果：HTTP 非 200 或 code≠0
        """
        resp = kyt_api.approve("nonexistent_case_99999")
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"


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

    @pytest.mark.regression
    def test_reject_missing_reject_type(self, kyt_api):
        """TC-KYT-205 Reject 缺少 rejectType，返回参数错误
        前置条件：无
        请求体：缺少 rejectType，其余字段完整
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = kyt_api.post("/v1/kyt/case/test_case_001/reject", json={
            "caseId": "test_case_001",
            "refundResult": "RefundNow",
            "refundAddress": "0xREFUND_ADDR",
        })
        assert resp.status_code in [400, 422] or resp.json().get("code") != 0, \
            f"实际 {resp.status_code}，响应：{resp.json()}"

    @pytest.mark.regression
    def test_reject_no_refund(self, kyt_api):
        """TC-KYT-206 Reject + NoRefund（不退款场景，无需 refundAddress）
        前置条件：存在 test_txn_pending_005 测试数据
        请求体：rejectType=Freeze，refundResult=NoRefund，不传 refundAddress
        预期结果：HTTP 200，code=0
        """
        resp = kyt_api.get_case("test_txn_pending_005")
        if resp.status_code == 404:
            pytest.skip("测试数据 test_txn_pending_005 不存在于当前环境")
        body = assert_success(resp)
        kyt_case_id = body["data"]["caseId"]

        resp = kyt_api.reject(
            kyt_case_id,
            reject_type=["Freeze"],
            refund_result="NoRefund",
            remark="冻结处理，无需退款",
        )
        assert_success(resp)

    @pytest.mark.regression
    def test_reject_nonexistent_case(self, kyt_api):
        """TC-KYT-207 Reject 不存在的 caseId，返回业务错误
        前置条件：无
        请求：POST /v1/kyt/case/nonexistent_case_99999/reject，携带完整请求体
        预期结果：HTTP 非 200 或 code≠0
        """
        resp = kyt_api.reject(
            "nonexistent_case_99999",
            reject_type=["Refund"],
            refund_result="RefundNow",
            refund_address="0xREFUND_ADDR",
        )
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"


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

    @pytest.mark.regression
    def test_collect_travel_rule_missing_txn_type(self, kyt_api):
        """TC-KYT-404 缺少 txnType，返回业务错误
        前置条件：无
        请求体：缺少 txnType，其余字段完整
        预期结果：code=9999 或 HTTP 400/422
        """
        resp = kyt_api.post("/v1/kyt/travel-rule/check", json={
            "merchantOrderId": "xuanhaojun_uat_2026041606",
            "legalEntity": "PDCA",
            "amount": "2.26",
            "ccy": "USDT",
            "protocol": "ETHEREUM",
        })
        body = resp.json()
        assert body.get("code") == "9999" or resp.status_code in [400, 422], \
            f"实际 {resp.status_code}，响应：{body}"

    @pytest.mark.regression
    def test_collect_travel_rule_missing_ccy(self, kyt_api):
        """TC-KYT-405 缺少 ccy，返回业务错误
        前置条件：无
        请求体：缺少 ccy，其余字段完整
        预期结果：code=9999 或 HTTP 400/422
        """
        resp = kyt_api.post("/v1/kyt/travel-rule/check", json={
            "merchantOrderId": "xuanhaojun_uat_2026041606",
            "txnType": "SMART_PAYMENT",
            "legalEntity": "PDCA",
            "amount": "2.26",
            "protocol": "ETHEREUM",
        })
        body = resp.json()
        assert body.get("code") == "9999" or resp.status_code in [400, 422], \
            f"实际 {resp.status_code}，响应：{body}"

    @pytest.mark.regression
    def test_collect_travel_rule_missing_protocol(self, kyt_api):
        """TC-KYT-406 缺少 protocol，返回业务错误
        前置条件：无
        请求体：缺少 protocol，其余字段完整
        预期结果：code=9999 或 HTTP 400/422
        """
        resp = kyt_api.post("/v1/kyt/travel-rule/check", json={
            "merchantOrderId": "xuanhaojun_uat_2026041606",
            "txnType": "SMART_PAYMENT",
            "legalEntity": "PDCA",
            "amount": "2.26",
            "ccy": "USDT",
        })
        body = resp.json()
        assert body.get("code") == "9999" or resp.status_code in [400, 422], \
            f"实际 {resp.status_code}，响应：{body}"

    @pytest.mark.regression
    def test_collect_travel_rule_missing_legal_entity(self, kyt_api):
        """TC-KYT-407 缺少 legalEntity，返回业务错误
        前置条件：无
        请求体：缺少 legalEntity，其余字段完整
        预期结果：code=9999 或 HTTP 400/422
        """
        resp = kyt_api.post("/v1/kyt/travel-rule/check", json={
            "merchantOrderId": "xuanhaojun_uat_2026041606",
            "txnType": "SMART_PAYMENT",
            "amount": "2.26",
            "ccy": "USDT",
            "protocol": "ETHEREUM",
        })
        body = resp.json()
        assert body.get("code") == "9999" or resp.status_code in [400, 422], \
            f"实际 {resp.status_code}，响应：{body}"

    @pytest.mark.regression
    def test_collect_travel_rule_amount_zero(self, kyt_api):
        """TC-KYT-408 amount 为 0，返回业务错误
        前置条件：无
        请求体：amount=0，其余字段完整
        预期结果：code=9999 或 HTTP 400/422（金额必须大于0）
        """
        resp = kyt_api.post("/v1/kyt/travel-rule/check", json={
            "merchantOrderId": "xuanhaojun_uat_2026041606",
            "txnType": "SMART_PAYMENT",
            "legalEntity": "PDCA",
            "amount": "0",
            "ccy": "USDT",
            "protocol": "ETHEREUM",
        })
        body = resp.json()
        assert body.get("code") == "9999" or resp.status_code in [400, 422], \
            f"实际 {resp.status_code}，响应：{body}"

    @pytest.mark.regression
    def test_collect_travel_rule_amount_negative(self, kyt_api):
        """TC-KYT-409 amount 为负数，返回业务错误
        前置条件：无
        请求体：amount=-1，其余字段完整
        预期结果：code=9999 或 HTTP 400/422
        """
        resp = kyt_api.post("/v1/kyt/travel-rule/check", json={
            "merchantOrderId": "xuanhaojun_uat_2026041606",
            "txnType": "SMART_PAYMENT",
            "legalEntity": "PDCA",
            "amount": "-1",
            "ccy": "USDT",
            "protocol": "ETHEREUM",
        })
        body = resp.json()
        assert body.get("code") == "9999" or resp.status_code in [400, 422], \
            f"实际 {resp.status_code}，响应：{body}"


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

    @pytest.mark.regression
    def test_complete_ln_case_invalid_result(self, kyt_api):
        """TC-KYT-303 LN Case 排查 result 值非法，返回参数错误
        前置条件：无
        请求体：result=InvalidValue（非 Pass/Fail 枚举值）
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = kyt_api.post("/v1/kyt/ln-case/test_ln_case_001/review", json={
            "result": "InvalidValue",
            "remark": "测试非法枚举值",
        })
        assert resp.status_code in [400, 422] or resp.json().get("code") != 0, \
            f"实际 {resp.status_code}，响应：{resp.json()}"

    @pytest.mark.regression
    def test_complete_ln_case_missing_result(self, kyt_api):
        """TC-KYT-304 LN Case 排查缺少 result，返回参数错误
        前置条件：无
        请求体：缺少 result 字段
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = kyt_api.post("/v1/kyt/ln-case/test_ln_case_001/review", json={
            "remark": "缺少 result 字段",
        })
        assert resp.status_code in [400, 422] or resp.json().get("code") != 0, \
            f"实际 {resp.status_code}，响应：{resp.json()}"

    @pytest.mark.regression
    def test_complete_ln_case_nonexistent(self, kyt_api):
        """TC-KYT-305 不存在的 lnCaseId 提交排查结果，返回业务错误
        前置条件：无
        请求：POST /v1/kyt/ln-case/nonexistent_ln_case_99999/review
        预期结果：HTTP 非 200 或 code≠0
        """
        resp = kyt_api.complete_ln_case(
            "nonexistent_ln_case_99999",
            result="Pass",
            remark="不存在的 LN Case",
        )
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"


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
