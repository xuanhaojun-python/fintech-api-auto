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

    @pytest.mark.regression
    def test_allocate_address_missing_payment_link_info(self, address_api):
        """TC-ADDR-002 缺少 paymentLinkInfo，返回参数错误
        前置条件：无
        请求体：addressPurpose=PAYMENT_LINK，但不传 paymentLinkInfo
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = address_api.post("/v1/addresses/allocate", json={
            "merchantOrderId": "xuanhaojun_uat_2026041606",
            "protocol": "ETHEREUM",
            "addressPurpose": "PAYMENT_LINK",
            "legalEntity": "PDCA",
            "travelRuleInfo": _VALID_TRAVEL_RULE_INFO,
        })
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"

    @pytest.mark.regression
    def test_allocate_address_duplicate_order(self, address_api):
        """TC-ADDR-003 重复分配同一 merchantOrderId（幂等性验证）
        前置条件：TC-ADDR-001 已成功执行，merchantOrderId 已存在
        请求：相同 merchantOrderId 再次分配
        预期结果：返回已分配地址（幂等）或业务错误，不应报 500
        """
        resp = address_api.allocate_address(
            merchant_order_id="xuanhaojun_uat_2026041606",
            protocol="ETHEREUM",
            address_purpose="PAYMENT_LINK",
            legal_entity="PDCA",
            payment_link_info=_VALID_PAYMENT_LINK_INFO,
            travel_rule_info=_VALID_TRAVEL_RULE_INFO,
        )
        assert resp.status_code != 500, f"重复分配不应返回 500，实际：{resp.status_code}"


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

    @pytest.mark.regression
    def test_check_eligibility_invalid_header(self, address_api, bene_id):
        """TC-ADDR-303 X-ON-BEHALF-OF 传入无效 accountId，返回未授权或账户不存在
        前置条件：已有有效 beneId
        请求：X-ON-BEHALF-OF 传入不存在的 accountId
        预期结果：HTTP 400/401/403/404 或 code≠0
        """
        resp = address_api.get(
            f"/v1/address-ownership/eligibility/{bene_id}",
            headers={"X-ON-BEHALF-OF": "invalid_account_id_000"},
        )
        body = resp.json()
        assert resp.status_code in [400, 401, 403, 404] or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"


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

    @pytest.mark.regression
    def test_create_ownership_case_missing_ccy(self, address_api, bene_id):
        """TC-ADDR-402 缺少 ccy，返回参数错误
        前置条件：已有有效 beneId
        请求体：缺少 ccy，其余字段完整
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = address_api.post(
            "/v1/address-ownership/cases",
            headers={"X-ON-BEHALF-OF": "ACC2003701647536205824"},
            json={"beneId": bene_id, "protocol": "ETHEREUM"},
        )
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"

    @pytest.mark.regression
    def test_create_ownership_case_missing_protocol(self, address_api, bene_id):
        """TC-ADDR-403 缺少 protocol，返回参数错误
        前置条件：已有有效 beneId
        请求体：缺少 protocol，其余字段完整
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = address_api.post(
            "/v1/address-ownership/cases",
            headers={"X-ON-BEHALF-OF": "ACC2003701647536205824"},
            json={"beneId": bene_id, "ccy": "USDT"},
        )
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"

    @pytest.mark.regression
    def test_create_ownership_case_invalid_header(self, address_api, bene_id):
        """TC-ADDR-404 X-ON-BEHALF-OF 传入无效 accountId，返回未授权或账户不存在
        前置条件：已有有效 beneId
        请求：X-ON-BEHALF-OF 传入不存在的 accountId
        预期结果：HTTP 400/401/403/404 或 code≠0
        """
        resp = address_api.post(
            "/v1/address-ownership/cases",
            headers={"X-ON-BEHALF-OF": "invalid_account_id_000"},
            json={"beneId": bene_id, "ccy": "USDT", "protocol": "ETHEREUM"},
        )
        body = resp.json()
        assert resp.status_code in [400, 401, 403, 404] or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"


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

    @pytest.mark.regression
    def test_get_case_invalid_header(self, address_api, bene_id):
        """TC-ADDR-503 X-ON-BEHALF-OF 传入无效 accountId，返回未授权或账户不存在
        前置条件：已有有效 beneId
        请求：X-ON-BEHALF-OF 传入不存在的 accountId
        预期结果：HTTP 400/401/403/404 或 code≠0
        """
        resp = address_api.get(
            f"/v1/address-ownership/cases/benes/{bene_id}",
            headers={"X-ON-BEHALF-OF": "invalid_account_id_000"},
        )
        body = resp.json()
        assert resp.status_code in [400, 401, 403, 404] or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"


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


class TestCreateDepositAddress:
    """创建入金地址：POST /v1/address/deposit"""

    @pytest.mark.smoke
    def test_create_deposit_address(self, address_api):
        """TC-ADDR-701 正常创建入金地址
        前置条件：无
        请求体：ccy=USDT, protocol=ETHEREUM, address=有效以太坊地址
        预期结果：HTTP 200，code=0，返回 addressId
        """
        resp = address_api.create_deposit_address(
            ccy="USDT",
            protocol="ETHEREUM",
            address="0x43F9Ed2B614DF4F59217EAEAF7806b2147b67B7D",
        )
        print(f"\n[TC-ADDR-701] 响应状态码: {resp.status_code}")
        print(f"[TC-ADDR-701] 响应体: {resp.json()}")
        assert_success(resp)

    @pytest.mark.regression
    def test_create_deposit_address_with_nickname(self, address_api):
        """TC-ADDR-702 携带 nickName 正常创建入金地址
        前置条件：无
        请求体：必填字段 + nickName=测试入金地址
        预期结果：HTTP 200，code=0
        """
        resp = address_api.create_deposit_address(
            ccy="USDT",
            protocol="TRON",
            address="TRx9V5aBd123456789012345678901234567",
            nick_name="测试入金地址",
        )
        print(f"\n[TC-ADDR-702] 响应状态码: {resp.status_code}")
        print(f"[TC-ADDR-702] 响应体: {resp.json()}")
        assert_success(resp)

    @pytest.mark.regression
    def test_create_deposit_address_missing_ccy(self, address_api):
        """TC-ADDR-703 缺少 ccy，返回参数错误
        请求体：缺少 ccy，其余字段完整
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = address_api.post("/v1/address/deposit", json={
            "protocol": "ETHEREUM",
            "address": "0x43F9Ed2B614DF4F59217EAEAF7806b2147b67B7D",
        })
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"

    @pytest.mark.regression
    def test_create_deposit_address_missing_protocol(self, address_api):
        """TC-ADDR-704 缺少 protocol，返回参数错误
        请求体：缺少 protocol，其余字段完整
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = address_api.post("/v1/address/deposit", json={
            "ccy": "USDT",
            "address": "0x43F9Ed2B614DF4F59217EAEAF7806b2147b67B7D",
        })
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"

    @pytest.mark.regression
    def test_create_deposit_address_missing_address(self, address_api):
        """TC-ADDR-705 缺少 address，返回参数错误
        请求体：缺少 address，其余字段完整
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = address_api.post("/v1/address/deposit", json={
            "ccy": "USDT",
            "protocol": "ETHEREUM",
        })
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"


class TestGetDepositAddress:
    """查询入金地址：GET /v1/address/deposit/{addressId}"""

    @pytest.mark.smoke
    def test_get_deposit_address(self, address_api):
        """TC-ADDR-801 先创建再查询，验证返回正确
        前置条件：无
        步骤：创建入金地址 → 取 addressId → 查询
        预期结果：HTTP 200，code=0，address 字段非空
        """
        create_resp = address_api.create_deposit_address(
            ccy="USDT",
            protocol="ETHEREUM",
            address="0x43F9Ed2B614DF4F59217EAEAF7806b2147b67B7D",
        )
        if create_resp.status_code != 200 or create_resp.json().get("code") != 0:
            pytest.skip("创建入金地址失败，跳过查询测试")
        address_id = create_resp.json()["data"]["addressId"]

        resp = address_api.get_deposit_address(address_id=address_id)
        body = assert_success(resp)
        assert body["data"].get("address"), "响应中 address 字段不应为空"

    @pytest.mark.regression
    def test_get_deposit_address_nonexistent(self, address_api):
        """TC-ADDR-802 查询不存在的 addressId，返回错误
        请求：GET /v1/address/deposit/nonexistent_id_99999
        预期结果：HTTP 非 200 或 code≠0
        """
        resp = address_api.get_deposit_address(address_id="nonexistent_id_99999")
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"


class TestListDepositAddresses:
    """分页查询入金地址：PUT /v1/address/deposit"""

    @pytest.mark.smoke
    def test_list_deposit_addresses(self, address_api):
        """TC-ADDR-901 正常分页查询入金地址
        请求：pageIndex=1, pageSize=20，无过滤条件
        预期结果：HTTP 200，code=0，返回 list 字段
        """
        resp = address_api.list_deposit_addresses(page_index=1, page_size=20)
        body = assert_success(resp)
        assert "list" in body.get("data", {}), "响应 data 中应包含 list 字段"

    @pytest.mark.regression
    def test_list_deposit_addresses_filter_by_ccy(self, address_api):
        """TC-ADDR-902 按 ccy 过滤查询入金地址
        请求：ccy=USDT，pageIndex=1, pageSize=10
        预期结果：HTTP 200，code=0，返回结果中 ccy 均为 USDT
        """
        resp = address_api.list_deposit_addresses(ccy="USDT", page_index=1, page_size=10)
        body = assert_success(resp)
        items = body.get("data", {}).get("list", [])
        for item in items:
            assert item.get("ccy") == "USDT", f"过滤后结果 ccy 应为 USDT，实际：{item.get('ccy')}"


class TestCreateWithdrawAddress:
    """创建出金地址：POST /v1/address/withdraw"""

    @pytest.mark.smoke
    def test_create_withdraw_address(self, address_api):
        """TC-ADDR-1001 正常创建出金地址
        请求体：ccy=USDT, chain=ETHEREUM, address=有效以太坊地址
        预期结果：HTTP 200，code=0
        """
        resp = address_api.create_withdraw_address(
            ccy="USDT",
            chain="ETHEREUM",
            address="0x43F9Ed2B614DF4F59217EAEAF7806b2147b67B7D",
        )
        print(f"\n[TC-ADDR-1001] 响应状态码: {resp.status_code}")
        print(f"[TC-ADDR-1001] 响应体: {resp.json()}")
        assert_success(resp)

    @pytest.mark.regression
    def test_create_withdraw_address_with_nickname(self, address_api):
        """TC-ADDR-1002 携带 nickName 正常创建出金地址
        请求体：必填字段 + nickName=测试出金地址
        预期结果：HTTP 200，code=0
        """
        resp = address_api.create_withdraw_address(
            ccy="USDT",
            chain="TRON",
            address="TRx9V5aBd123456789012345678901234567",
            nick_name="测试出金地址",
        )
        assert_success(resp)

    @pytest.mark.regression
    def test_create_withdraw_address_missing_ccy(self, address_api):
        """TC-ADDR-1003 缺少 ccy，返回参数错误
        请求体：缺少 ccy，其余字段完整
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = address_api.post("/v1/address/withdraw", json={
            "chain": "ETHEREUM",
            "address": "0x43F9Ed2B614DF4F59217EAEAF7806b2147b67B7D",
        })
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"

    @pytest.mark.regression
    def test_create_withdraw_address_missing_chain(self, address_api):
        """TC-ADDR-1004 缺少 chain，返回参数错误
        请求体：缺少 chain，其余字段完整
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = address_api.post("/v1/address/withdraw", json={
            "ccy": "USDT",
            "address": "0x43F9Ed2B614DF4F59217EAEAF7806b2147b67B7D",
        })
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"

    @pytest.mark.regression
    def test_create_withdraw_address_missing_address(self, address_api):
        """TC-ADDR-1005 缺少 address，返回参数错误
        请求体：缺少 address，其余字段完整
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = address_api.post("/v1/address/withdraw", json={
            "ccy": "USDT",
            "chain": "ETHEREUM",
        })
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"


class TestDispatchDepositAddresses:
    """批量分配客户入金地址：POST /v1/account/deposit-address/dispatch"""

    @pytest.mark.smoke
    def test_dispatch_deposit_addresses(self, address_api):
        """TC-ADDR-1101 正常批量分配入金地址
        请求体：包含一条有效分配记录
        预期结果：HTTP 200，code=0
        """
        resp = address_api.dispatch_deposit_addresses(items=[
            {"ccy": "USDT", "protocol": "ETHEREUM", "accountId": "ACC2003701647536205824"},
        ])
        print(f"\n[TC-ADDR-1101] 响应状态码: {resp.status_code}")
        print(f"[TC-ADDR-1101] 响应体: {resp.json()}")
        assert_success(resp)

    @pytest.mark.regression
    def test_dispatch_deposit_addresses_empty_list(self, address_api):
        """TC-ADDR-1102 空列表，返回参数错误
        请求体：[]
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = address_api.dispatch_deposit_addresses(items=[])
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"

    @pytest.mark.regression
    def test_dispatch_deposit_addresses_missing_account_id(self, address_api):
        """TC-ADDR-1103 分配记录中缺少 accountId，返回参数错误
        请求体：items 中缺少 accountId 字段
        预期结果：HTTP 400/422 或 code≠0
        """
        resp = address_api.dispatch_deposit_addresses(items=[
            {"ccy": "USDT", "protocol": "ETHEREUM"},
        ])
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0, \
            f"实际 {resp.status_code}，响应：{body}"
