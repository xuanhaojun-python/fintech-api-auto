"""
充值交易查询接口测试
接口：GET /v1/txns/deposit/{txnId}

实际响应结构：
{
  "code": "0000",
  "data": {
    "txnId": "PIT...",
    "ccy": "USDT",
    "amount": "0.100000",
    "status": "SUCCEEDED",
    "type": "PAYMENT_LINK",
    "createdAt": 1773990157330,
    "chainInfo": {
      "sourceAddress": "0x...",
      "destinationAddress": "0x...",
      "txnHash": "0x...",
      "chain": "ETHEREUM"
    },
    "accountId": "ACC...",
    "payer": {"sourceAddress": "0x..."},
    "verificationByManual": true
  }
}
"""
import pytest

from utils.assertions import assert_success, assert_response_time

VALID_TXN_ID = "PIT2034888323293515776"


class TestGetDepositTxn:
    """查询充值交易 GET /v1/txns/deposit/{txnId}"""

    @pytest.mark.smoke
    def test_get_deposit_txn_success(self, txn_api):
        """TC-TXN-DEP-001 查询已存在的充值交易，返回成功
        预期结果：HTTP 200，code=0000，data 包含 txnId
        """
        resp = txn_api.get_deposit_txn(VALID_TXN_ID)
        print(f"\n[TC-TXN-DEP-001] {resp.status_code} {resp.json()}")
        body = assert_success(resp)
        assert body.get("data") is not None, f"data 不应为空：{body}"

    @pytest.mark.regression
    def test_get_deposit_txn_id_matches(self, txn_api):
        """TC-TXN-DEP-002 响应中 txnId 与请求一致"""
        resp = txn_api.get_deposit_txn(VALID_TXN_ID)
        data = assert_success(resp).get("data", {})
        assert data.get("txnId") == VALID_TXN_ID, \
            f"txnId 应为 {VALID_TXN_ID}，实际：{data.get('txnId')}"

    @pytest.mark.regression
    def test_get_deposit_txn_response_structure(self, txn_api):
        """TC-TXN-DEP-003 响应包含所有关键字段
        预期结果：txnId、ccy、amount、status、type、createdAt、accountId 均存在
        """
        resp = txn_api.get_deposit_txn(VALID_TXN_ID)
        data = assert_success(resp).get("data", {})
        for field in ("txnId", "ccy", "amount", "status", "type", "createdAt", "accountId"):
            assert field in data, f"响应缺少字段 {field}：{data}"

    @pytest.mark.regression
    def test_get_deposit_txn_amount_positive(self, txn_api):
        """TC-TXN-DEP-004 amount 大于 0"""
        resp = txn_api.get_deposit_txn(VALID_TXN_ID)
        data = assert_success(resp).get("data", {})
        assert float(data.get("amount", 0)) > 0, \
            f"amount 应大于 0，实际：{data.get('amount')}"

    @pytest.mark.regression
    def test_get_deposit_txn_ccy_not_empty(self, txn_api):
        """TC-TXN-DEP-005 ccy 不为空"""
        resp = txn_api.get_deposit_txn(VALID_TXN_ID)
        data = assert_success(resp).get("data", {})
        assert data.get("ccy"), f"ccy 不应为空：{data}"

    @pytest.mark.regression
    def test_get_deposit_txn_status_not_empty(self, txn_api):
        """TC-TXN-DEP-006 status 不为空"""
        resp = txn_api.get_deposit_txn(VALID_TXN_ID)
        data = assert_success(resp).get("data", {})
        assert data.get("status"), f"status 不应为空：{data}"

    @pytest.mark.regression
    def test_get_deposit_txn_created_at_timestamp(self, txn_api):
        """TC-TXN-DEP-007 createdAt 为 13 位毫秒时间戳"""
        resp = txn_api.get_deposit_txn(VALID_TXN_ID)
        data = assert_success(resp).get("data", {})
        created_at = data.get("createdAt", 0)
        assert isinstance(created_at, int) and len(str(created_at)) == 13, \
            f"createdAt 应为 13 位时间戳，实际：{created_at}"

    @pytest.mark.regression
    def test_get_deposit_txn_chain_info_structure(self, txn_api):
        """TC-TXN-DEP-008 chainInfo 包含 sourceAddress、destinationAddress、txnHash、chain"""
        resp = txn_api.get_deposit_txn(VALID_TXN_ID)
        data = assert_success(resp).get("data", {})
        chain_info = data.get("chainInfo", {})
        for field in ("sourceAddress", "destinationAddress", "txnHash", "chain"):
            assert field in chain_info, f"chainInfo 缺少字段 {field}：{chain_info}"

    @pytest.mark.regression
    def test_get_deposit_txn_txn_hash_not_empty(self, txn_api):
        """TC-TXN-DEP-009 chainInfo.txnHash 不为空"""
        resp = txn_api.get_deposit_txn(VALID_TXN_ID)
        data = assert_success(resp).get("data", {})
        txn_hash = data.get("chainInfo", {}).get("txnHash", "")
        assert txn_hash, f"txnHash 不应为空：{data.get('chainInfo')}"

    @pytest.mark.regression
    def test_get_deposit_txn_idempotent(self, txn_api):
        """TC-TXN-DEP-010 连续查询两次，结果一致（幂等）"""
        resp1 = txn_api.get_deposit_txn(VALID_TXN_ID)
        resp2 = txn_api.get_deposit_txn(VALID_TXN_ID)
        data1 = assert_success(resp1).get("data", {})
        data2 = assert_success(resp2).get("data", {})
        assert data1.get("txnId") == data2.get("txnId"), \
            f"两次查询 txnId 不一致：{data1.get('txnId')} vs {data2.get('txnId')}"
        assert data1.get("status") == data2.get("status"), \
            f"两次查询 status 不一致：{data1.get('status')} vs {data2.get('status')}"

    @pytest.mark.regression
    def test_get_deposit_txn_response_time(self, txn_api):
        """TC-TXN-DEP-011 接口响应时间在 2000ms 以内"""
        resp = txn_api.get_deposit_txn(VALID_TXN_ID)
        assert_success(resp)
        assert_response_time(resp, max_ms=2000)

    @pytest.mark.regression
    def test_get_deposit_txn_nonexistent(self, txn_api):
        """TC-TXN-DEP-101 查询不存在的 txnId，返回 404
        预期结果：HTTP 404，code=000004
        """
        resp = txn_api.get_deposit_txn("PIT0000000000000000000")
        print(f"\n[TC-TXN-DEP-101] {resp.status_code} {resp.json()}")
        assert resp.status_code == 404, \
            f"不存在的交易应返回 404，实际：{resp.status_code}"
        assert resp.json().get("code") == "000004", \
            f"code 应为 000004，实际：{resp.json()}"

    @pytest.mark.regression
    def test_get_deposit_txn_invalid_format(self, txn_api):
        """TC-TXN-DEP-102 传入非 PIT 格式的 txnId，返回 404"""
        resp = txn_api.get_deposit_txn("invalid_txn_id_001")
        print(f"\n[TC-TXN-DEP-102] {resp.status_code} {resp.json()}")
        assert resp.status_code in [400, 404], \
            f"非法格式 txnId 应返回 4xx，实际：{resp.status_code}，响应：{resp.json()}"


class TestListDepositTxns:
    """分页查询充值交易列表 POST /v1/txns/deposit

    响应结构：
    {
      "code": "0000",
      "data": {
        "sum": 158,
        "pageIndex": 1,
        "pageSize": 10,
        "records": [
          {"txnId": "PIT...", "ccy": "USDT", "amount": "...", "status": "SUCCEEDED",
           "type": "SMART_PAYMENT", "createdAt": ..., "chainInfo": {...},
           "accountId": "ACC...", "payer": {...}}
        ]
      }
    }
    """

    @pytest.mark.smoke
    def test_list_deposit_txns_success(self, txn_api):
        """TC-TXN-LIST-001 分页查询充值交易列表，返回成功
        预期结果：HTTP 200，data 包含 records 和 sum
        """
        resp = txn_api.list_deposit_txns(page_index=1, page_size=10)
        print(f"\n[TC-TXN-LIST-001] {resp.status_code}")
        body = assert_success(resp)
        data = body.get("data", {})
        assert "records" in data, f"data 缺少 records 字段：{data}"
        assert "sum" in data, f"data 缺少 sum 字段：{data}"

    @pytest.mark.regression
    def test_list_deposit_txns_records_is_list(self, txn_api):
        """TC-TXN-LIST-002 records 为列表类型"""
        resp = txn_api.list_deposit_txns(page_index=1, page_size=10)
        data = assert_success(resp).get("data", {})
        assert isinstance(data.get("records"), list), \
            f"records 应为列表，实际：{type(data.get('records'))}"

    @pytest.mark.regression
    def test_list_deposit_txns_sum_is_int(self, txn_api):
        """TC-TXN-LIST-003 sum 为整数且 >= 0"""
        resp = txn_api.list_deposit_txns(page_index=1, page_size=10)
        data = assert_success(resp).get("data", {})
        assert isinstance(data.get("sum"), int) and data["sum"] >= 0, \
            f"sum 应为非负整数，实际：{data.get('sum')}"

    @pytest.mark.regression
    def test_list_deposit_txns_sum_gte_records(self, txn_api):
        """TC-TXN-LIST-004 sum 大于等于 records 长度"""
        resp = txn_api.list_deposit_txns(page_index=1, page_size=10)
        data = assert_success(resp).get("data", {})
        assert data["sum"] >= len(data["records"]), \
            f"sum({data['sum']}) 应 >= records 长度({len(data['records'])})"

    @pytest.mark.regression
    def test_list_deposit_txns_page_size_limits_records(self, txn_api):
        """TC-TXN-LIST-005 pageSize=5，返回 records 长度 <= 5"""
        resp = txn_api.list_deposit_txns(page_index=1, page_size=5)
        data = assert_success(resp).get("data", {})
        assert len(data.get("records", [])) <= 5, \
            f"pageSize=5 时 records 长度应 <= 5，实际：{len(data.get('records', []))}"

    @pytest.mark.regression
    def test_list_deposit_txns_page_index_echoed(self, txn_api):
        """TC-TXN-LIST-006 响应中 pageIndex 与请求一致"""
        resp = txn_api.list_deposit_txns(page_index=2, page_size=10)
        data = assert_success(resp).get("data", {})
        assert data.get("pageIndex") == 2, \
            f"pageIndex 应为 2，实际：{data.get('pageIndex')}"

    @pytest.mark.regression
    def test_list_deposit_txns_record_structure(self, txn_api):
        """TC-TXN-LIST-007 records 中每条记录包含关键字段"""
        resp = txn_api.list_deposit_txns(page_index=1, page_size=10)
        data = assert_success(resp).get("data", {})
        for record in data.get("records", []):
            for field in ("txnId", "ccy", "amount", "status", "type", "createdAt", "accountId"):
                assert field in record, f"记录缺少字段 {field}：{record}"

    @pytest.mark.regression
    def test_list_deposit_txns_amount_positive(self, txn_api):
        """TC-TXN-LIST-008 每条记录 amount > 0"""
        resp = txn_api.list_deposit_txns(page_index=1, page_size=10)
        data = assert_success(resp).get("data", {})
        for record in data.get("records", []):
            assert float(record.get("amount", 0)) > 0, \
                f"amount 应大于 0：{record}"

    @pytest.mark.regression
    def test_list_deposit_txns_response_time(self, txn_api):
        """TC-TXN-LIST-009 接口响应时间在 3000ms 以内"""
        resp = txn_api.list_deposit_txns(page_index=1, page_size=10)
        assert_success(resp)
        assert_response_time(resp, max_ms=3000)

    @pytest.mark.regression
    def test_list_deposit_txns_page2_different_from_page1(self, txn_api):
        """TC-TXN-LIST-010 第 2 页与第 1 页记录不同（翻页正确）
        前置条件：总记录数 > pageSize
        """
        resp1 = txn_api.list_deposit_txns(page_index=1, page_size=5)
        resp2 = txn_api.list_deposit_txns(page_index=2, page_size=5)
        data1 = assert_success(resp1).get("data", {})
        data2 = assert_success(resp2).get("data", {})
        if data1["sum"] <= 5:
            pytest.skip("总记录数 <= 5，无法验证翻页")
        ids1 = {r["txnId"] for r in data1.get("records", [])}
        ids2 = {r["txnId"] for r in data2.get("records", [])}
        assert ids1.isdisjoint(ids2), f"第 1 页和第 2 页不应有重复记录：{ids1 & ids2}"

    @pytest.mark.regression
    def test_list_deposit_txns_missing_page_index(self, txn_api):
        """TC-TXN-LIST-101 缺少 pageIndex，返回 400 或使用默认值"""
        resp = txn_api.post("/v1/txns/deposit", json={"pageSize": 10})
        print(f"\n[TC-TXN-LIST-101] {resp.status_code} {resp.json()}")
        assert resp.status_code < 500, f"不应返回 5xx，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_list_deposit_txns_missing_page_size(self, txn_api):
        """TC-TXN-LIST-102 缺少 pageSize，返回 400 或使用默认值"""
        resp = txn_api.post("/v1/txns/deposit", json={"pageIndex": 1})
        print(f"\n[TC-TXN-LIST-102] {resp.status_code} {resp.json()}")
        assert resp.status_code < 500, f"不应返回 5xx，实际：{resp.status_code}"
