"""
入金地址管理接口测试
覆盖：创建入金地址、查询单个入金地址、分页查询入金地址

实际响应结构（data）：
{
  "addressId": "CPAYER...",
  "travelRuleCaseId": "TRC...",
  "addressType": "PAYER",
  "accountId": "ACC...",
  "nickName": "...",
  "ccy": "USDT",
  "protocol": "ETHEREUM",
  "address": "0x...",
  "whitelisted": false,
  "status": "CREATED",
  "addressVerificationResult": "PENDING",
  "legalEntity": "PLANCKAGE_PL",
  "createdAt": 1790674133135
}
"""
import uuid

import pytest

from utils.assertions import assert_success, assert_response_time

VALID_ADDRESS = "0xFaACa42785813fc7057c2A3013e3307979160b35"
VALID_ADDRESS_ID = "CPAYER2104865989760958464"


def _address():
    """生成唯一以太坊格式地址（测试用）"""
    suffix = uuid.uuid4().hex[:38]
    return f"0x{suffix}"


class TestCreateDepositAddress:
    """创建入金地址 POST /v1/address/deposit"""

    @pytest.mark.smoke
    def test_create_deposit_address_success(self, address_api):
        """TC-DEP-CREATE-001 正常创建 USDT/ETHEREUM 入金地址
        预期结果：HTTP 200，data 包含 addressId、status=CREATED
        """
        resp = address_api.create_deposit_address(
            ccy="USDT",
            protocol="ETHEREUM",
            address=_address(),
            nick_name="test_create_001",
        )
        print(f"\n[TC-DEP-CREATE-001] {resp.status_code} {resp.json()}")
        body = assert_success(resp)
        data = body.get("data", {})
        assert data.get("addressId"), f"addressId 不应为空：{data}"
        assert data.get("status") == "CREATED", f"status 应为 CREATED：{data.get('status')}"

    @pytest.mark.regression
    def test_create_deposit_address_response_structure(self, address_api):
        """TC-DEP-CREATE-002 响应结构包含所有关键字段
        预期结果：addressId、ccy、protocol、address、addressType、whitelisted、createdAt 均存在
        """
        resp = address_api.create_deposit_address(
            ccy="USDT",
            protocol="ETHEREUM",
            address=_address(),
        )
        data = assert_success(resp).get("data", {})
        for field in ("addressId", "ccy", "protocol", "address",
                      "addressType", "whitelisted", "createdAt", "status"):
            assert field in data, f"响应缺少字段 {field}：{data}"

    @pytest.mark.regression
    def test_create_deposit_address_ccy_matches(self, address_api):
        """TC-DEP-CREATE-003 响应中 ccy 与请求一致"""
        resp = address_api.create_deposit_address(
            ccy="USDT",
            protocol="ETHEREUM",
            address=_address(),
        )
        data = assert_success(resp).get("data", {})
        assert data.get("ccy") == "USDT", f"ccy 应为 USDT，实际：{data.get('ccy')}"

    @pytest.mark.regression
    def test_create_deposit_address_protocol_matches(self, address_api):
        """TC-DEP-CREATE-004 响应中 protocol 与请求一致"""
        resp = address_api.create_deposit_address(
            ccy="USDT",
            protocol="ETHEREUM",
            address=_address(),
        )
        data = assert_success(resp).get("data", {})
        assert data.get("protocol") == "ETHEREUM", \
            f"protocol 应为 ETHEREUM，实际：{data.get('protocol')}"

    @pytest.mark.regression
    def test_create_deposit_address_address_type_is_payer(self, address_api):
        """TC-DEP-CREATE-005 响应中 addressType 为 PAYER"""
        resp = address_api.create_deposit_address(
            ccy="USDT",
            protocol="ETHEREUM",
            address=_address(),
        )
        data = assert_success(resp).get("data", {})
        assert data.get("addressType") == "PAYER", \
            f"addressType 应为 PAYER，实际：{data.get('addressType')}"

    @pytest.mark.regression
    def test_create_deposit_address_initial_whitelisted_false(self, address_api):
        """TC-DEP-CREATE-006 新创建地址 whitelisted 默认为 false"""
        resp = address_api.create_deposit_address(
            ccy="USDT",
            protocol="ETHEREUM",
            address=_address(),
        )
        data = assert_success(resp).get("data", {})
        assert data.get("whitelisted") is False, \
            f"新建地址 whitelisted 应为 false，实际：{data.get('whitelisted')}"

    @pytest.mark.regression
    def test_create_deposit_address_with_nick_name(self, address_api):
        """TC-DEP-CREATE-007 传入 nickName，响应中 nickName 与请求一致"""
        nick = f"nick_{uuid.uuid4().hex[:8]}"
        resp = address_api.create_deposit_address(
            ccy="USDT",
            protocol="ETHEREUM",
            address=_address(),
            nick_name=nick,
        )
        data = assert_success(resp).get("data", {})
        assert data.get("nickName") == nick, \
            f"nickName 应为 {nick}，实际：{data.get('nickName')}"

    @pytest.mark.regression
    def test_create_deposit_address_created_at_timestamp(self, address_api):
        """TC-DEP-CREATE-008 createdAt 为 13 位毫秒时间戳"""
        resp = address_api.create_deposit_address(
            ccy="USDT",
            protocol="ETHEREUM",
            address=_address(),
        )
        data = assert_success(resp).get("data", {})
        created_at = data.get("createdAt", 0)
        assert isinstance(created_at, int) and len(str(created_at)) == 13, \
            f"createdAt 应为 13 位时间戳，实际：{created_at}"

    @pytest.mark.regression
    def test_create_deposit_address_response_time(self, address_api):
        """TC-DEP-CREATE-009 接口响应时间在 3000ms 以内"""
        resp = address_api.create_deposit_address(
            ccy="USDT",
            protocol="ETHEREUM",
            address=_address(),
        )
        assert_success(resp)
        assert_response_time(resp, max_ms=3000)

    @pytest.mark.regression
    def test_create_deposit_address_missing_ccy(self, address_api):
        """TC-DEP-CREATE-101 缺少 ccy 字段，返回 400"""
        resp = address_api.post(
            "/v1/address/deposit",
            json={"protocol": "ETHEREUM", "address": _address()},
        )
        print(f"\n[TC-DEP-CREATE-101] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"缺少 ccy 应返回 400，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_create_deposit_address_missing_protocol(self, address_api):
        """TC-DEP-CREATE-102 缺少 protocol 字段，返回 400"""
        resp = address_api.post(
            "/v1/address/deposit",
            json={"ccy": "USDT", "address": _address()},
        )
        print(f"\n[TC-DEP-CREATE-102] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"缺少 protocol 应返回 400，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_create_deposit_address_missing_address(self, address_api):
        """TC-DEP-CREATE-103 缺少 address 字段，返回 400"""
        resp = address_api.post(
            "/v1/address/deposit",
            json={"ccy": "USDT", "protocol": "ETHEREUM"},
        )
        print(f"\n[TC-DEP-CREATE-103] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"缺少 address 应返回 400，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_create_deposit_address_invalid_protocol(self, address_api):
        """TC-DEP-CREATE-104 protocol 传入不支持的值，返回 400"""
        resp = address_api.create_deposit_address(
            ccy="USDT",
            protocol="INVALID_CHAIN",
            address=_address(),
        )
        print(f"\n[TC-DEP-CREATE-104] {resp.status_code} {resp.json()}")
        assert resp.status_code in [400, 422], \
            f"无效 protocol 应返回 4xx，实际：{resp.status_code}"


class TestGetDepositAddress:
    """查询单个入金地址 GET /v1/address/deposit/{addressId}"""

    @pytest.mark.smoke
    def test_get_deposit_address_success(self, address_api):
        """TC-DEP-GET-001 查询已存在的入金地址，返回成功
        预期结果：HTTP 200，data.addressId 与请求一致
        """
        resp = address_api.get_deposit_address(VALID_ADDRESS_ID)
        print(f"\n[TC-DEP-GET-001] {resp.status_code} {resp.json()}")
        body = assert_success(resp)
        data = body.get("data", {})
        assert data.get("addressId") == VALID_ADDRESS_ID, \
            f"addressId 应为 {VALID_ADDRESS_ID}，实际：{data.get('addressId')}"

    @pytest.mark.regression
    def test_get_deposit_address_structure(self, address_api):
        """TC-DEP-GET-002 响应包含所有关键字段"""
        resp = address_api.get_deposit_address(VALID_ADDRESS_ID)
        data = assert_success(resp).get("data", {})
        for field in ("addressId", "ccy", "protocol", "address",
                      "addressType", "whitelisted", "status", "createdAt"):
            assert field in data, f"响应缺少字段 {field}：{data}"

    @pytest.mark.regression
    def test_get_deposit_address_ccy_not_empty(self, address_api):
        """TC-DEP-GET-003 响应中 ccy 不为空"""
        resp = address_api.get_deposit_address(VALID_ADDRESS_ID)
        data = assert_success(resp).get("data", {})
        assert data.get("ccy"), f"ccy 不应为空：{data}"

    @pytest.mark.regression
    def test_get_deposit_address_address_not_empty(self, address_api):
        """TC-DEP-GET-004 响应中 address 不为空"""
        resp = address_api.get_deposit_address(VALID_ADDRESS_ID)
        data = assert_success(resp).get("data", {})
        assert data.get("address"), f"address 不应为空：{data}"

    @pytest.mark.regression
    def test_get_deposit_address_idempotent(self, address_api):
        """TC-DEP-GET-005 连续查询两次，结果一致（幂等）"""
        resp1 = address_api.get_deposit_address(VALID_ADDRESS_ID)
        resp2 = address_api.get_deposit_address(VALID_ADDRESS_ID)
        data1 = assert_success(resp1).get("data", {})
        data2 = assert_success(resp2).get("data", {})
        assert data1.get("addressId") == data2.get("addressId"), \
            f"两次查询 addressId 不一致：{data1} vs {data2}"
        assert data1.get("status") == data2.get("status"), \
            f"两次查询 status 不一致：{data1.get('status')} vs {data2.get('status')}"

    @pytest.mark.regression
    def test_get_deposit_address_nonexistent(self, address_api):
        """TC-DEP-GET-006 查询不存在的 addressId，返回业务错误"""
        resp = address_api.get_deposit_address("CPAYER0000000000000000000")
        print(f"\n[TC-DEP-GET-006] {resp.status_code} {resp.json()}")
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != "0000", \
            f"不存在的地址应返回错误，实际：{resp.status_code}，响应：{body}"

    @pytest.mark.regression
    def test_get_deposit_address_response_time(self, address_api):
        """TC-DEP-GET-007 接口响应时间在 2000ms 以内"""
        resp = address_api.get_deposit_address(VALID_ADDRESS_ID)
        assert_success(resp)
        assert_response_time(resp, max_ms=2000)


class TestListDepositAddresses:
    """分页查询入金地址 PUT /v1/address/deposit"""

    @pytest.mark.smoke
    def test_list_default_pagination(self, address_api):
        """TC-DEP-LIST-001 默认分页查询，返回 records 和 total"""
        resp = address_api.list_deposit_addresses(page_index=1, page_size=20)
        print(f"\n[TC-DEP-LIST-001] {resp.status_code} {resp.json()}")
        body = assert_success(resp)
        data = body.get("data", {})
        assert "records" in data, "响应 data 中缺少 records 字段"
        assert "total" in data, "响应 data 中缺少 total 字段"
        assert isinstance(data["records"], list), "records 应为列表"
        assert isinstance(data["total"], int), "total 应为整数"

    @pytest.mark.regression
    def test_list_total_gte_records_count(self, address_api):
        """TC-DEP-LIST-002 total 大于等于 records 长度"""
        resp = address_api.list_deposit_addresses(page_index=1, page_size=20)
        data = assert_success(resp).get("data", {})
        assert data["total"] >= len(data["records"]), \
            f"total({data['total']}) 应 >= records 长度({len(data['records'])})"

    @pytest.mark.regression
    def test_list_filter_by_ccy(self, address_api):
        """TC-DEP-LIST-003 按 ccy=USDT 过滤，返回记录均为 USDT"""
        resp = address_api.list_deposit_addresses(ccy="USDT", page_index=1, page_size=20)
        data = assert_success(resp).get("data", {})
        for record in data.get("records", []):
            assert record.get("ccy") == "USDT", \
                f"过滤 ccy=USDT 但返回了 {record.get('ccy')}：{record}"

    @pytest.mark.regression
    def test_list_page_size_limits_records(self, address_api):
        """TC-DEP-LIST-004 pageSize=1，返回 records 长度 <= 1"""
        resp = address_api.list_deposit_addresses(page_index=1, page_size=1)
        data = assert_success(resp).get("data", {})
        assert len(data.get("records", [])) <= 1, \
            f"pageSize=1 时 records 长度应 <= 1，实际：{len(data.get('records', []))}"

    @pytest.mark.regression
    def test_list_records_structure(self, address_api):
        """TC-DEP-LIST-005 records 中每条记录包含关键字段"""
        resp = address_api.list_deposit_addresses(page_index=1, page_size=10)
        data = assert_success(resp).get("data", {})
        for record in data.get("records", []):
            for field in ("addressId", "ccy", "protocol", "address", "status"):
                assert field in record, f"记录缺少字段 {field}：{record}"

    @pytest.mark.regression
    def test_list_response_time(self, address_api):
        """TC-DEP-LIST-006 接口响应时间在 3000ms 以内"""
        resp = address_api.list_deposit_addresses(page_index=1, page_size=20)
        assert_success(resp)
        assert_response_time(resp, max_ms=3000)

    @pytest.mark.regression
    def test_list_filter_by_address(self, address_api):
        """TC-DEP-LIST-007 按 address 精确过滤，返回对应记录"""
        resp = address_api.list_deposit_addresses(
            address=VALID_ADDRESS, page_index=1, page_size=10
        )
        data = assert_success(resp).get("data", {})
        for record in data.get("records", []):
            assert record.get("address") == VALID_ADDRESS, \
                f"过滤 address 返回了不匹配的记录：{record}"

    @pytest.mark.regression
    def test_list_nonexistent_address_returns_empty(self, address_api):
        """TC-DEP-LIST-008 按不存在的 address 过滤，返回空列表"""
        resp = address_api.list_deposit_addresses(
            address="0x0000000000000000000000000000000000000000",
            page_index=1, page_size=10
        )
        data = assert_success(resp).get("data", {})
        assert data.get("records") == [], \
            f"不存在的地址过滤应返回空列表，实际：{data.get('records')}"
        assert data.get("total") == 0, \
            f"不存在的地址过滤 total 应为 0，实际：{data.get('total')}"


RECHARGE_ACCOUNT_ID = "ACC1996532313185505280"


class TestGetRechargeAddresses:
    """查询充值地址 GET /v1/address/deposit

    响应结构：
    {
      "code": "0000",
      "data": [
        {"ccy": "USDC", "chain": "ETHEREUM", "address": "0x..."},
        {"ccy": "USDT", "chain": "ETHEREUM", "address": "0x..."}
      ]
    }
    """

    @pytest.mark.smoke
    def test_get_recharge_addresses_success(self, address_api):
        """TC-RECHARGE-001 查询充值地址，返回成功
        预期结果：HTTP 200，data 为列表
        """
        resp = address_api.get_recharge_addresses(account_id=RECHARGE_ACCOUNT_ID)
        print(f"\n[TC-RECHARGE-001] {resp.status_code} {resp.json()}")
        body = assert_success(resp)
        assert isinstance(body.get("data"), list), \
            f"data 应为列表，实际：{body.get('data')}"

    @pytest.mark.regression
    def test_get_recharge_addresses_data_not_empty(self, address_api):
        """TC-RECHARGE-002 返回的充值地址列表不为空
        前置条件：账户已配置充值地址
        """
        resp = address_api.get_recharge_addresses(account_id=RECHARGE_ACCOUNT_ID)
        data = assert_success(resp).get("data", [])
        assert len(data) > 0, f"充值地址列表不应为空：{data}"

    @pytest.mark.regression
    def test_get_recharge_addresses_record_structure(self, address_api):
        """TC-RECHARGE-003 每条记录包含 ccy、chain、address 字段"""
        resp = address_api.get_recharge_addresses(account_id=RECHARGE_ACCOUNT_ID)
        data = assert_success(resp).get("data", [])
        for item in data:
            for field in ("ccy", "chain", "address"):
                assert field in item, f"记录缺少字段 {field}：{item}"

    @pytest.mark.regression
    def test_get_recharge_addresses_address_not_empty(self, address_api):
        """TC-RECHARGE-004 每条记录的 address 不为空字符串"""
        resp = address_api.get_recharge_addresses(account_id=RECHARGE_ACCOUNT_ID)
        data = assert_success(resp).get("data", [])
        for item in data:
            assert item.get("address"), f"address 不应为空：{item}"

    @pytest.mark.regression
    def test_get_recharge_addresses_ccy_not_empty(self, address_api):
        """TC-RECHARGE-005 每条记录的 ccy 不为空字符串"""
        resp = address_api.get_recharge_addresses(account_id=RECHARGE_ACCOUNT_ID)
        data = assert_success(resp).get("data", [])
        for item in data:
            assert item.get("ccy"), f"ccy 不应为空：{item}"

    @pytest.mark.regression
    def test_get_recharge_addresses_chain_not_empty(self, address_api):
        """TC-RECHARGE-006 每条记录的 chain 不为空字符串"""
        resp = address_api.get_recharge_addresses(account_id=RECHARGE_ACCOUNT_ID)
        data = assert_success(resp).get("data", [])
        for item in data:
            assert item.get("chain"), f"chain 不应为空：{item}"

    @pytest.mark.regression
    def test_get_recharge_addresses_idempotent(self, address_api):
        """TC-RECHARGE-007 连续查询两次，结果一致（幂等）"""
        resp1 = address_api.get_recharge_addresses(account_id=RECHARGE_ACCOUNT_ID)
        resp2 = address_api.get_recharge_addresses(account_id=RECHARGE_ACCOUNT_ID)
        data1 = assert_success(resp1).get("data", [])
        data2 = assert_success(resp2).get("data", [])
        addrs1 = {(i["ccy"], i["chain"], i["address"]) for i in data1}
        addrs2 = {(i["ccy"], i["chain"], i["address"]) for i in data2}
        assert addrs1 == addrs2, f"两次查询结果不一致：{addrs1} vs {addrs2}"

    @pytest.mark.regression
    def test_get_recharge_addresses_response_time(self, address_api):
        """TC-RECHARGE-008 接口响应时间在 2000ms 以内"""
        resp = address_api.get_recharge_addresses(account_id=RECHARGE_ACCOUNT_ID)
        assert_success(resp)
        assert_response_time(resp, max_ms=2000)

    @pytest.mark.regression
    def test_get_recharge_addresses_without_header(self, address_api):
        """TC-RECHARGE-009 不传 X-ON-BEHALF-OF，使用主账户查询
        预期结果：HTTP 200，返回主账户充值地址
        """
        resp = address_api.get_recharge_addresses()
        print(f"\n[TC-RECHARGE-009] {resp.status_code} {resp.json()}")
        body = assert_success(resp)
        assert isinstance(body.get("data"), list), \
            f"data 应为列表，实际：{body.get('data')}"

    @pytest.mark.regression
    def test_get_recharge_addresses_nonexistent_account(self, address_api):
        """TC-RECHARGE-010 传入不存在的 accountId，返回 404
        预期结果：HTTP 404，code=000029
        """
        resp = address_api.get_recharge_addresses(account_id="ACC0000000000000000000")
        print(f"\n[TC-RECHARGE-010] {resp.status_code} {resp.json()}")
        assert resp.status_code == 404, \
            f"不存在账户应返回 404，实际：{resp.status_code}，响应：{resp.json()}"
        assert resp.json().get("code") == "000029", \
            f"code 应为 000029，实际：{resp.json()}"

    @pytest.mark.regression
    def test_get_recharge_addresses_invalid_account_format(self, address_api):
        """TC-RECHARGE-011 传入非法格式 accountId，返回 4xx"""
        resp = address_api.get_recharge_addresses(account_id="invalid_id_001")
        print(f"\n[TC-RECHARGE-011] {resp.status_code} {resp.json()}")
        assert resp.status_code in [400, 401, 403, 404], \
            f"非法格式 accountId 应返回 4xx，实际：{resp.status_code}，响应：{resp.json()}"
