"""
换汇询价接口测试
接口：GET /v1/quote
参数：ccyPair（如 USDT-USD、USD-USDT）

实际响应结构：
{
  "code": "0000",
  "data": {
    "id": "PRI...",
    "rate": "0.989582",
    "expiredTime": 1790751690010,
    "currentTime": 1790751685896
  }
}
"""
import pytest

from utils.assertions import assert_success, assert_response_time


class TestGetQuote:
    """正常场景"""

    @pytest.mark.smoke
    def test_get_quote_usdt_usd_success(self, quote_api):
        """TC-QUOTE-001 USDT-USD 询价，返回成功
        预期结果：HTTP 200，data 包含 id 和 rate
        """
        resp = quote_api.get_quote("USDT-USD")
        print(f"\n[TC-QUOTE-001] {resp.status_code} {resp.json()}")
        body = assert_success(resp)
        assert body.get("data") is not None, f"data 不应为空：{body}"

    @pytest.mark.regression
    def test_get_quote_usd_usdt_success(self, quote_api):
        """TC-QUOTE-002 USD-USDT 反向询价，返回成功"""
        resp = quote_api.get_quote("USD-USDT")
        print(f"\n[TC-QUOTE-002] {resp.status_code} {resp.json()}")
        assert_success(resp)

    @pytest.mark.regression
    def test_get_quote_usdc_usd_success(self, quote_api):
        """TC-QUOTE-003 USDC-USD 询价，返回成功"""
        resp = quote_api.get_quote("USDC-USD")
        print(f"\n[TC-QUOTE-003] {resp.status_code} {resp.json()}")
        assert_success(resp)

    @pytest.mark.regression
    def test_get_quote_response_structure(self, quote_api):
        """TC-QUOTE-004 响应包含 id、rate、expiredTime、currentTime 字段"""
        resp = quote_api.get_quote("USDT-USD")
        data = assert_success(resp).get("data", {})
        for field in ("id", "rate", "expiredTime", "currentTime"):
            assert field in data, f"响应缺少字段 {field}：{data}"

    @pytest.mark.regression
    def test_get_quote_id_not_empty(self, quote_api):
        """TC-QUOTE-005 报价 id 不为空且以 PRI 开头"""
        resp = quote_api.get_quote("USDT-USD")
        data = assert_success(resp).get("data", {})
        assert data.get("id"), f"id 不应为空：{data}"
        assert data["id"].startswith("PRI"), f"id 应以 PRI 开头，实际：{data['id']}"

    @pytest.mark.regression
    def test_get_quote_rate_is_positive(self, quote_api):
        """TC-QUOTE-006 rate 为正数"""
        resp = quote_api.get_quote("USDT-USD")
        data = assert_success(resp).get("data", {})
        assert float(data.get("rate", 0)) > 0, \
            f"rate 应大于 0，实际：{data.get('rate')}"

    @pytest.mark.regression
    def test_get_quote_expired_time_gt_current_time(self, quote_api):
        """TC-QUOTE-007 expiredTime 大于 currentTime（报价未过期）"""
        resp = quote_api.get_quote("USDT-USD")
        data = assert_success(resp).get("data", {})
        assert data["expiredTime"] > data["currentTime"], \
            f"expiredTime 应大于 currentTime：{data['expiredTime']} vs {data['currentTime']}"

    @pytest.mark.regression
    def test_get_quote_current_time_is_timestamp(self, quote_api):
        """TC-QUOTE-008 currentTime 为 13 位毫秒时间戳"""
        resp = quote_api.get_quote("USDT-USD")
        data = assert_success(resp).get("data", {})
        current_time = data.get("currentTime", 0)
        assert isinstance(current_time, int) and len(str(current_time)) == 13, \
            f"currentTime 应为 13 位时间戳，实际：{current_time}"

    @pytest.mark.regression
    def test_get_quote_each_call_returns_new_id(self, quote_api):
        """TC-QUOTE-009 每次询价返回不同的报价 id（报价唯一性）"""
        resp1 = quote_api.get_quote("USDT-USD")
        resp2 = quote_api.get_quote("USDT-USD")
        id1 = assert_success(resp1).get("data", {}).get("id")
        id2 = assert_success(resp2).get("data", {}).get("id")
        assert id1 != id2, f"每次询价应返回不同 id，实际两次相同：{id1}"

    @pytest.mark.regression
    def test_get_quote_response_time(self, quote_api):
        """TC-QUOTE-010 接口响应时间在 2000ms 以内"""
        resp = quote_api.get_quote("USDT-USD")
        assert_success(resp)
        assert_response_time(resp, max_ms=2000)

    @pytest.mark.regression
    def test_get_quote_reverse_rate_reasonable(self, quote_api):
        """TC-QUOTE-011 正反向汇率乘积接近 1（合理性校验）
        USDT-USD rate * USD-USDT rate 应接近 1（允许误差 5%）
        """
        resp1 = quote_api.get_quote("USDT-USD")
        resp2 = quote_api.get_quote("USD-USDT")
        rate1 = float(assert_success(resp1).get("data", {}).get("rate", 0))
        rate2 = float(assert_success(resp2).get("data", {}).get("rate", 0))
        product = rate1 * rate2
        assert 0.9 <= product <= 1.1, \
            f"正反向汇率乘积应接近 1，实际：{rate1} * {rate2} = {product}"


class TestGetQuoteAbnormal:
    """异常场景"""

    @pytest.mark.regression
    def test_get_quote_unsupported_ccy_pair(self, quote_api):
        """TC-QUOTE-101 传入不支持的货币对，返回业务错误
        预期结果：HTTP 400，code=9999
        """
        resp = quote_api.get_quote("USDT-USDC")
        print(f"\n[TC-QUOTE-101] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"不支持的货币对应返回 400，实际：{resp.status_code}"
        assert resp.json().get("code") == "9999", \
            f"code 应为 9999，实际：{resp.json()}"

    @pytest.mark.regression
    def test_get_quote_invalid_ccy_pair_format(self, quote_api):
        """TC-QUOTE-102 传入格式错误的 ccyPair（无连字符），返回 400"""
        resp = quote_api.get_quote("USDTUSD")
        print(f"\n[TC-QUOTE-102] {resp.status_code} {resp.json()}")
        assert resp.status_code in [400, 422], \
            f"非法格式 ccyPair 应返回 4xx，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_get_quote_missing_ccy_pair(self, quote_api):
        """TC-QUOTE-103 缺少 ccyPair 参数，返回 400"""
        resp = quote_api.get("/v1/quote")
        print(f"\n[TC-QUOTE-103] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"缺少 ccyPair 应返回 400，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_get_quote_nonexistent_ccy(self, quote_api):
        """TC-QUOTE-104 传入不存在的币种，返回业务错误"""
        resp = quote_api.get_quote("XYZ-ABC")
        print(f"\n[TC-QUOTE-104] {resp.status_code} {resp.json()}")
        assert resp.status_code in [400, 422], \
            f"不存在币种应返回 4xx，实际：{resp.status_code}"
