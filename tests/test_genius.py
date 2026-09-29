"""
流量卡购买状态查询接口测试
接口：GET /v1/genius/purchase-conf
响应：data 为列表，每条包含 cardId（流量卡ID）和 buy（是否已购买）
"""
import pytest

from utils.assertions import assert_success, assert_response_time


class TestGetPurchaseConf:
    """正常场景"""

    @pytest.mark.smoke
    def test_get_purchase_conf_success(self, genius_api):
        """TC-GENIUS-001 查询流量卡购买状态，返回成功且包含卡列表"""
        resp = genius_api.get_purchase_conf()
        print(f"\n[TC-GENIUS-001] 响应状态码: {resp.status_code}")
        print(f"[TC-GENIUS-001] 响应体: {resp.json()}")
        body = assert_success(resp)
        assert isinstance(body.get("data"), list), f"data 应为列表，实际：{body.get('data')}"
        assert_response_time(resp, max_ms=2000)

    @pytest.mark.regression
    def test_purchase_conf_data_structure(self, genius_api):
        """TC-GENIUS-002 返回的每条流量卡数据包含 cardId 和 buy 字段"""
        resp = genius_api.get_purchase_conf()
        body = assert_success(resp)
        data = body.get("data", [])
        for item in data:
            assert "cardId" in item, f"缺少 cardId 字段：{item}"
            assert "buy" in item, f"缺少 buy 字段：{item}"
            assert isinstance(item["buy"], bool), f"buy 应为 boolean，实际：{item['buy']}"

    @pytest.mark.regression
    def test_purchase_conf_data_not_empty(self, genius_api):
        """TC-GENIUS-003 data 列表不应为空
        前置条件：系统中已配置至少一张流量卡
        预期结果：data 列表长度 > 0
        """
        resp = genius_api.get_purchase_conf()
        body = assert_success(resp)
        data = body.get("data", [])
        assert len(data) > 0, "data 列表不应为空，系统中应至少有一张流量卡配置"

    @pytest.mark.regression
    def test_purchase_conf_card_id_not_empty(self, genius_api):
        """TC-GENIUS-004 每条记录的 cardId 不为空字符串
        预期结果：所有 cardId 均为非空字符串
        """
        resp = genius_api.get_purchase_conf()
        body = assert_success(resp)
        data = body.get("data", [])
        for item in data:
            assert item.get("cardId"), f"cardId 不应为空，实际：{item}"

    @pytest.mark.regression
    def test_purchase_conf_buy_is_boolean(self, genius_api):
        """TC-GENIUS-005 buy 字段只能为 true 或 false，不允许其他值
        预期结果：所有 buy 值均为 boolean 类型（True 或 False）
        """
        resp = genius_api.get_purchase_conf()
        body = assert_success(resp)
        data = body.get("data", [])
        for item in data:
            assert item.get("buy") in (True, False), \
                f"buy 应为 true/false，实际：{item.get('buy')}，记录：{item}"

    @pytest.mark.regression
    def test_purchase_conf_response_time(self, genius_api):
        """TC-GENIUS-006 接口响应时间应在 1000ms 以内
        预期结果：elapsed ≤ 1000ms
        """
        resp = genius_api.get_purchase_conf()
        assert_success(resp)
        assert_response_time(resp, max_ms=1000)

    @pytest.mark.regression
    def test_purchase_conf_idempotent(self, genius_api):
        """TC-GENIUS-007 连续调用两次，结果一致（幂等性）
        步骤：调用两次 GET /v1/genius/purchase-conf
        预期结果：两次返回的 data 列表长度及 cardId 集合相同
        """
        resp1 = genius_api.get_purchase_conf()
        resp2 = genius_api.get_purchase_conf()
        data1 = assert_success(resp1).get("data", [])
        data2 = assert_success(resp2).get("data", [])
        ids1 = {item["cardId"] for item in data1}
        ids2 = {item["cardId"] for item in data2}
        assert ids1 == ids2, f"两次调用 cardId 集合不一致：{ids1} vs {ids2}"


class TestGetPurchaseConfAbnormal:
    """异常场景"""

    @pytest.mark.regression
    def test_get_purchase_conf_forbidden_account(self, genius_api):
        """TC-GENIUS-101 无权限账户访问，返回 403"""
        resp = genius_api.get_purchase_conf(account_id="ACC1998628247771996160")
        assert resp.status_code == 403, f"期望 403，实际 {resp.status_code}"
        assert resp.json().get("code") == "000015", f"期望 code=000015，实际：{resp.json()}"

    @pytest.mark.regression
    def test_get_purchase_conf_invalid_account_id(self, genius_api):
        """TC-GENIUS-102 非 ACC 格式的无效 accountId，返回 400/401/403
        请求：X-ON-BEHALF-OF 传入非法格式 ID（如 invalid_id_001）
        预期结果：HTTP 400/401/403
        """
        resp = genius_api.get_purchase_conf(account_id="invalid_id_001")
        assert resp.status_code in [400, 401, 403], \
            f"非法 accountId 应返回 4xx，实际 {resp.status_code}，响应：{resp.json()}"

    @pytest.mark.regression
    def test_get_purchase_conf_nonexistent_account(self, genius_api):
        """TC-GENIUS-103 不存在的 accountId，返回 4xx 或业务错误
        请求：X-ON-BEHALF-OF 传入不存在的账户 ID（格式合法但不存在）
        预期结果：HTTP 400/401/403/404 或 code≠0
        """
        resp = genius_api.get_purchase_conf(account_id="ACC0000000000000000000")
        body = resp.json()
        assert resp.status_code in [400, 401, 403, 404] or body.get("code") not in (0, "0", "0000"), \
            f"不存在的账户应返回错误，实际 {resp.status_code}，响应：{body}"
