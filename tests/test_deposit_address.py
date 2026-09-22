"""
付款人地址管理接口测试
覆盖：查询单个入金地址、分页查询入金地址
"""
import pytest

from utils.assertions import assert_success


class TestGetDepositAddress:
    """查询单个入金地址 GET /v1/address/deposit/{addressId}"""

    @pytest.mark.smoke
    def test_get_deposit_address(self, address_api):
        """TC-DEP-GET-001 查询已存在的入金地址"""
        resp = address_api.get_deposit_address("CPAYER2072227535617261568")
        print(f"\n[TC-DEP-GET-001] 响应状态码: {resp.status_code}")
        print(f"[TC-DEP-GET-001] 响应体: {resp.json()}")
        body = resp.json()
        assert body.get("code") == "000023", f"期望 code=000023，实际: {body}"


class TestListDepositAddresses:
    """分页查询入金地址 PUT /v1/address/deposit"""

    @pytest.mark.smoke
    def test_list_default_pagination(self, address_api):
        """TC-DEP-001 默认分页查询，返回成功且包含 records 和 total 字段"""
        resp = address_api.list_deposit_addresses(page_index=1, page_size=20)
        print(f"\n[TC-DEP-001] 响应状态码: {resp.status_code}")
        print(f"[TC-DEP-001] 响应体: {resp.json()}")
        body = assert_success(resp)
        data = body.get("data", {})
        assert "records" in data, "响应 data 中缺少 records 字段"
        assert "total" in data, "响应 data 中缺少 total 字段"
        assert isinstance(data["records"], list), "records 应为列表"
        assert isinstance(data["total"], int), "total 应为整数"
