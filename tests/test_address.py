"""
地址分配接口测试
覆盖：根据订单分配地址
"""
import pytest

from utils.assertions import assert_success

_VALID_PAYMENT_LINK_INFO = {
    "payerName": "黄晓明",
    "payerId": "27",
    "orderAmount": "1.657",
    "ccy": "USDC",
    "protocol": "TRON",
    "title": "zhifu",
    "description": "描述信息",
    "finalPayee": "adipisicing do Lorem veniam",
    "linkType": "OPEN_AMOUNT",
    "expiryDate": "2026-12-06",
}

_VALID_TRAVEL_RULE_INFO = {
    "originatorVASPName": "黄晓明",
    "customerType": "CORPORATE",
    "originatorName": "黄晓明",
    "originatorAddress": "0x43F9Ed2B614DF4F59217EAEAF7806b2147b67B7D",
    "dateOfBirth": "2025-12-18",
    "occupation": "sit occaecat dolore",
    "country": "laboris consectetur velit",
    "city": "太汉市",
    "postalCode": "639951",
    "idType": "40",
    "idNumber": "18",
}


class TestAllocateAddress:
    """根据订单分配地址"""

    @pytest.mark.smoke
    def test_allocate_address(self, address_api):
        """TC-ADDR-001 正常分配地址"""
        resp = address_api.allocate_address(
            merchant_order_id="xuanhaojun_uat_2026041606",
            protocol="ETHEREUM",
            address_purpose="PAYMENT_LINK",
            legal_entity="PDCA",
            payment_link_info=_VALID_PAYMENT_LINK_INFO,
            travel_rule_info=_VALID_TRAVEL_RULE_INFO,
        )
        print(f"\n[TC-ADDR-001] 响应状态码: {resp.status_code}")
        print(f"[TC-ADDR-001] 响应体: {resp.json()}")
        assert_success(resp)


class TestAllocateAddressMissingFields:
    """缺少必填字段"""

    @pytest.mark.regression
    def test_missing_merchant_order_id(self, address_api):
        """TC-ADDR-101 缺少 merchantOrderId"""
        resp = address_api.post("/v1/addresses/allocate", json={
            "protocol": "ETHEREUM",
            "addressPurpose": "PAYMENT_LINK",
            "legalEntity": "PDCA",
            "paymentLinkInfo": _VALID_PAYMENT_LINK_INFO,
            "travelRuleInfo": _VALID_TRAVEL_RULE_INFO,
        })
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0

    @pytest.mark.regression
    def test_missing_protocol(self, address_api):
        """TC-ADDR-102 缺少 protocol"""
        resp = address_api.post("/v1/addresses/allocate", json={
            "merchantOrderId": "xuanhaojun_uat_2026041606",
            "addressPurpose": "PAYMENT_LINK",
            "legalEntity": "PDCA",
            "paymentLinkInfo": _VALID_PAYMENT_LINK_INFO,
            "travelRuleInfo": _VALID_TRAVEL_RULE_INFO,
        })
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0

    @pytest.mark.regression
    def test_missing_address_purpose(self, address_api):
        """TC-ADDR-103 缺少 addressPurpose"""
        resp = address_api.post("/v1/addresses/allocate", json={
            "merchantOrderId": "xuanhaojun_uat_2026041606",
            "protocol": "ETHEREUM",
            "legalEntity": "PDCA",
            "paymentLinkInfo": _VALID_PAYMENT_LINK_INFO,
            "travelRuleInfo": _VALID_TRAVEL_RULE_INFO,
        })
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0

    @pytest.mark.regression
    def test_missing_legal_entity(self, address_api):
        """TC-ADDR-104 缺少 legalEntity"""
        resp = address_api.post("/v1/addresses/allocate", json={
            "merchantOrderId": "xuanhaojun_uat_2026041606",
            "protocol": "ETHEREUM",
            "addressPurpose": "PAYMENT_LINK",
            "paymentLinkInfo": _VALID_PAYMENT_LINK_INFO,
            "travelRuleInfo": _VALID_TRAVEL_RULE_INFO,
        })
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0


class TestAllocateAddressInvalidEnum:
    """非法枚举值"""

    @pytest.mark.regression
    def test_invalid_protocol(self, address_api):
        """TC-ADDR-201 protocol 传入非法值"""
        resp = address_api.allocate_address(
            merchant_order_id="xuanhaojun_uat_2026041606",
            protocol="INVALID_CHAIN",
            address_purpose="PAYMENT_LINK",
            legal_entity="PDCA",
            payment_link_info=_VALID_PAYMENT_LINK_INFO,
            travel_rule_info=_VALID_TRAVEL_RULE_INFO,
        )
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0

    @pytest.mark.regression
    def test_invalid_address_purpose(self, address_api):
        """TC-ADDR-202 addressPurpose 传入非法值"""
        resp = address_api.allocate_address(
            merchant_order_id="xuanhaojun_uat_2026041606",
            protocol="ETHEREUM",
            address_purpose="INVALID_PURPOSE",
            legal_entity="PDCA",
            payment_link_info=_VALID_PAYMENT_LINK_INFO,
            travel_rule_info=_VALID_TRAVEL_RULE_INFO,
        )
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0


class TestAddressOwnershipEligibility:
    """地址所有权合格性检查"""

    @pytest.mark.smoke
    def test_check_eligibility(self, address_api, bene_id):
        """TC-ADDR-301 正常查询地址所有权合格性"""
        resp = address_api.check_address_ownership_eligibility(bene_id=bene_id)
        print(f"\n[TC-ADDR-301] beneId: {bene_id}")
        print(f"[TC-ADDR-301] 响应状态码: {resp.status_code}")
        print(f"[TC-ADDR-301] 响应体: {resp.json()}")
        assert_success(resp)

    @pytest.mark.regression
    def test_missing_bene_id(self, address_api):
        """TC-ADDR-302 缺少 beneId，返回错误"""
        resp = address_api.get("/v1/address-ownership/eligibility")
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0


class TestCreateOwnershipCase:
    """初始化地址所有权 Case"""

    @pytest.mark.smoke
    def test_create_ownership_case(self, address_api, bene_id):
        """TC-ADDR-401 正常初始化 Case 并返回 SDK 信息"""
        resp = address_api.create_ownership_case(
            bene_id=bene_id,
            ccy="USDT",
            protocol="ETHEREUM",
        )
        print(f"\n[TC-ADDR-401] beneId: {bene_id}")
        print(f"[TC-ADDR-401] 响应状态码: {resp.status_code}")
        print(f"[TC-ADDR-401] 响应体: {resp.json()}")
        assert_success(resp)


class TestGetCaseByBeneId:
    """根据 BeneId 查询 Case 信息"""

    @pytest.mark.smoke
    def test_get_case_by_bene_id(self, address_api, bene_id):
        """TC-ADDR-501 正常根据 BeneId 查询 Case 信息"""
        resp = address_api.get_case_by_bene_id(bene_id=bene_id)
        print(f"\n[TC-ADDR-501] beneId: {bene_id}")
        print(f"[TC-ADDR-501] 响应状态码: {resp.status_code}")
        print(f"[TC-ADDR-501] 响应体: {resp.json()}")
        assert_success(resp)

    @pytest.mark.regression
    def test_get_case_nonexistent_bene_id(self, address_api):
        """TC-ADDR-502 beneId 不存在，返回错误"""
        resp = address_api.get_case_by_bene_id(bene_id="nonexistent_bene_id_99999")
        body = resp.json()
        print(f"\n[TC-ADDR-502] 响应状态码: {resp.status_code}")
        print(f"[TC-ADDR-502] 响应体: {body}")
        assert resp.status_code != 200 or body.get("code") != 0


class TestReleaseAddress:
    """释放地址"""

    @pytest.mark.smoke
    def test_release_address(self, address_api, merchant_order_id):
        """TC-ADDR-601 正常释放地址"""
        resp = address_api.release_address(merchant_order_id=merchant_order_id)
        print(f"\n[TC-ADDR-601] merchantOrderId: {merchant_order_id}")
        print(f"[TC-ADDR-601] 响应状态码: {resp.status_code}")
        print(f"[TC-ADDR-601] 响应体: {resp.json()}")
        assert_success(resp)

    @pytest.mark.regression
    def test_release_nonexistent_order(self, address_api):
        """TC-ADDR-602 不存在的 merchantOrderId，返回错误"""
        resp = address_api.release_address(merchant_order_id="nonexistent_order_99999")
        body = resp.json()
        print(f"\n[TC-ADDR-602] 响应状态码: {resp.status_code}")
        print(f"[TC-ADDR-602] 响应体: {body}")
        assert resp.status_code != 200 or body.get("code") != 0

    @pytest.mark.regression
    def test_release_missing_order_id(self, address_api):
        """TC-ADDR-603 缺少 merchantOrderId，返回参数错误"""
        resp = address_api.post("/v1/addresses/release", json={})
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0
