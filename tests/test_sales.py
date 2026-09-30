"""
销售数据查询接口测试
接口：POST /v1/sales/query

实际响应结构：
{
  "code": "0000",
  "data": [
    {
      "id": "1",
      "trade_sales_no": "s029",
      "trade_sales_name": "包健",
      "create_month": "2026-01",
      "main_product_gmv": "950000.00000000",
      "total_kpi_amount_usd": "10000.00000000",
      ...
    }
  ]
}
"""
import pytest

from utils.assertions import assert_success, assert_response_time

SALES_ACCOUNT_ID = "ACC2000403724018839552"
VALID_TABLE = "ADS_SALES_KPI_PERFORMANCE_RESULT"


class TestQuerySalesNormal:
    """正常场景 POST /v1/sales/query"""

    @pytest.mark.smoke
    def test_query_sales_success(self, sales_api):
        """TC-SALES-001 查询销售数据，返回成功
        预期结果：HTTP 200，code=0000，data 为列表
        """
        resp = sales_api.query_sales(VALID_TABLE, SALES_ACCOUNT_ID, start_id=0, limit=2)
        print(f"\n[TC-SALES-001] {resp.status_code}")
        body = assert_success(resp)
        assert isinstance(body.get("data"), list), f"data 应为列表：{body}"

    @pytest.mark.regression
    def test_query_sales_data_not_empty(self, sales_api):
        """TC-SALES-002 data 返回非空列表"""
        resp = sales_api.query_sales(VALID_TABLE, SALES_ACCOUNT_ID, start_id=0, limit=2)
        data = assert_success(resp).get("data", [])
        assert len(data) > 0, "data 不应为空列表"

    @pytest.mark.regression
    def test_query_sales_limit_respected(self, sales_api):
        """TC-SALES-003 limit=2，返回记录数 <= 2"""
        resp = sales_api.query_sales(VALID_TABLE, SALES_ACCOUNT_ID, start_id=0, limit=2)
        data = assert_success(resp).get("data", [])
        assert len(data) <= 2, f"limit=2 时返回记录数应 <= 2，实际：{len(data)}"

    @pytest.mark.regression
    def test_query_sales_record_has_id(self, sales_api):
        """TC-SALES-004 每条记录包含 id 字段"""
        resp = sales_api.query_sales(VALID_TABLE, SALES_ACCOUNT_ID, start_id=0, limit=5)
        data = assert_success(resp).get("data", [])
        for record in data:
            assert "id" in record, f"记录缺少 id 字段：{record}"

    @pytest.mark.regression
    def test_query_sales_record_has_trade_sales_no(self, sales_api):
        """TC-SALES-005 每条记录包含 trade_sales_no 字段"""
        resp = sales_api.query_sales(VALID_TABLE, SALES_ACCOUNT_ID, start_id=0, limit=5)
        data = assert_success(resp).get("data", [])
        for record in data:
            assert "trade_sales_no" in record, f"记录缺少 trade_sales_no 字段：{record}"

    @pytest.mark.regression
    def test_query_sales_record_has_create_month(self, sales_api):
        """TC-SALES-006 每条记录包含 create_month 字段"""
        resp = sales_api.query_sales(VALID_TABLE, SALES_ACCOUNT_ID, start_id=0, limit=5)
        data = assert_success(resp).get("data", [])
        for record in data:
            assert "create_month" in record, f"记录缺少 create_month 字段：{record}"

    @pytest.mark.regression
    def test_query_sales_start_id_pagination(self, sales_api):
        """TC-SALES-007 start_id=0 与 start_id=1 返回不同数据（分页）"""
        resp1 = sales_api.query_sales(VALID_TABLE, SALES_ACCOUNT_ID, start_id=0, limit=1)
        resp2 = sales_api.query_sales(VALID_TABLE, SALES_ACCOUNT_ID, start_id=1, limit=1)
        data1 = assert_success(resp1).get("data", [])
        data2 = assert_success(resp2).get("data", [])
        if not data1 or not data2:
            pytest.skip("数据不足，无法验证分页")
        assert data1[0].get("id") != data2[0].get("id"), \
            f"start_id=0 与 start_id=1 应返回不同记录"

    @pytest.mark.regression
    def test_query_sales_limit_1(self, sales_api):
        """TC-SALES-008 limit=1，只返回 1 条记录"""
        resp = sales_api.query_sales(VALID_TABLE, SALES_ACCOUNT_ID, start_id=0, limit=1)
        data = assert_success(resp).get("data", [])
        assert len(data) == 1, f"limit=1 时应返回 1 条，实际：{len(data)}"

    @pytest.mark.regression
    def test_query_sales_idempotent(self, sales_api):
        """TC-SALES-009 相同参数查询两次，结果一致（幂等）"""
        resp1 = sales_api.query_sales(VALID_TABLE, SALES_ACCOUNT_ID, start_id=0, limit=2)
        resp2 = sales_api.query_sales(VALID_TABLE, SALES_ACCOUNT_ID, start_id=0, limit=2)
        data1 = assert_success(resp1).get("data", [])
        data2 = assert_success(resp2).get("data", [])
        assert [r.get("id") for r in data1] == [r.get("id") for r in data2], \
            "相同参数两次查询结果应一致"

    @pytest.mark.regression
    def test_query_sales_response_time(self, sales_api):
        """TC-SALES-010 接口响应时间在 3000ms 以内"""
        resp = sales_api.query_sales(VALID_TABLE, SALES_ACCOUNT_ID, start_id=0, limit=10)
        assert_success(resp)
        assert_response_time(resp, max_ms=3000)

    @pytest.mark.regression
    def test_query_sales_gmv_is_numeric(self, sales_api):
        """TC-SALES-011 main_product_gmv 为可转换为浮点数的字符串"""
        resp = sales_api.query_sales(VALID_TABLE, SALES_ACCOUNT_ID, start_id=0, limit=5)
        data = assert_success(resp).get("data", [])
        for record in data:
            gmv = record.get("main_product_gmv")
            if gmv is not None:
                assert float(gmv) >= 0, f"main_product_gmv 应为非负数，实际：{gmv}"

    @pytest.mark.regression
    def test_query_sales_total_kpi_is_numeric(self, sales_api):
        """TC-SALES-012 total_kpi_amount_usd 为可转换为浮点数的字符串"""
        resp = sales_api.query_sales(VALID_TABLE, SALES_ACCOUNT_ID, start_id=0, limit=5)
        data = assert_success(resp).get("data", [])
        for record in data:
            kpi = record.get("total_kpi_amount_usd")
            if kpi is not None:
                assert float(kpi) >= 0, f"total_kpi_amount_usd 应为非负数，实际：{kpi}"


class TestQuerySalesAbnormal:
    """异常场景 POST /v1/sales/query"""

    @pytest.mark.regression
    def test_query_sales_missing_table_name(self, sales_api):
        """TC-SALES-101 缺少 tableName，返回 400"""
        resp = sales_api.post(
            "/v1/sales/query",
            headers={"X-ON-BEHALF-OF": SALES_ACCOUNT_ID},
            json={"startId": 0, "limit": 10},
        )
        print(f"\n[TC-SALES-101] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"缺少 tableName 应返回 400，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_query_sales_missing_limit(self, sales_api):
        """TC-SALES-102 缺少 limit，返回 400"""
        resp = sales_api.post(
            "/v1/sales/query",
            headers={"X-ON-BEHALF-OF": SALES_ACCOUNT_ID},
            json={"tableName": VALID_TABLE, "startId": 0},
        )
        print(f"\n[TC-SALES-102] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"缺少 limit 应返回 400，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_query_sales_invalid_table_name(self, sales_api):
        """TC-SALES-103 tableName 传入不存在的表，返回 400"""
        resp = sales_api.query_sales("INVALID_TABLE_NAME", SALES_ACCOUNT_ID,
                                     start_id=0, limit=10)
        print(f"\n[TC-SALES-103] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"非法 tableName 应返回 400，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_query_sales_missing_account_id(self, sales_api):
        """TC-SALES-104 缺少 X-ON-BEHALF-OF header，返回 4xx"""
        resp = sales_api.post(
            "/v1/sales/query",
            json={"tableName": VALID_TABLE, "startId": 0, "limit": 10},
        )
        print(f"\n[TC-SALES-104] {resp.status_code} {resp.json()}")
        assert resp.status_code in [400, 401, 403, 404], \
            f"缺少账户 ID 应返回 4xx，实际：{resp.status_code}"
