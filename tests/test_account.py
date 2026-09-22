"""
账户状态查询接口测试
接口：POST /v1/account/status
"""
import uuid

import pytest

from utils.assertions import assert_success, assert_error, assert_field, assert_response_time, assert_account_status, assert_schema
import schemas.account as account_schema


class TestAccountStatusNormal:
    """正常场景：验证各种账户状态返回正确"""


    @pytest.mark.smoke
    def test_query_valid_account(self, account_api, accounts):
        """TC-AS-001 查询存在的有效账户，返回成功且包含完整字段"""
        acc = accounts["valid"]
        resp = account_api.get_status(acc["externalAccountId"], acc["registeredEmail"])
        body = assert_success(resp)
        assert_schema(body, account_schema.GET_ACCOUNT_STATUS)
        assert_field(body, "data", "status")
        assert_response_time(resp, max_ms=2000)

    @pytest.mark.smoke
    def test_account_status_active(self, account_api, accounts):
        """TC-AS-002 Active 账户状态正确返回"""
        acc = accounts["active"]
        resp = account_api.get_status(acc["externalAccountId"], acc["registeredEmail"])
        body = assert_success(resp)
        assert_account_status(body, "Active")

    @pytest.mark.regression
    def test_account_status_suspended(self, account_api, accounts):
        """TC-AS-003 Suspended 账户状态正确返回"""
        acc = accounts["suspended"]
        resp = account_api.get_status(acc["externalAccountId"], acc["registeredEmail"])
        body = assert_success(resp)
        assert_account_status(body, "Suspended")

    @pytest.mark.regression
    def test_account_status_close(self, account_api, accounts):
        """TC-AS-004 closed账户状态正确返回"""
        acc = accounts["closed"]
        resp = account_api.get_status(acc["externalAccountId"], acc["registeredEmail"])
        body = assert_success(resp)
        assert_account_status(body, "closed")

    @pytest.mark.regression
    def test_account_status_withdraw_only(self, account_api, accounts):
        """TC-AS-005 Withdraw Only 账户：canWithdraw=True，canDeposit=False"""
        acc = accounts["withdraw_only"]
        resp = account_api.get_status(acc["externalAccountId"], acc["registeredEmail"])
        body = assert_success(resp)
        assert_account_status(body, "Withdraw Only")
        data = body.get("data", {})
        assert data.get("canDeposit") is False, f"Withdraw Only 账户不应能入金，实际={data.get('canDeposit')}"
        assert data.get("canWithdraw") is True, f"Withdraw Only 账户应能出金，实际={data.get('canWithdraw')}"

    @pytest.mark.regression
    def test_smart_payment_enabled(self, account_api, accounts):
        """TC-AS-006 已开通 Smart Payment 的账户返回 smartPaymentEnabled=True"""
        acc = accounts["smart_payment_enabled"]
        resp = account_api.get_status(acc["externalAccountId"], acc["registeredEmail"])
        body = assert_success(resp)
        assert body.get("data", {}).get("smartPaymentEnabled") is True

    @pytest.mark.regression
    def test_pdca_account(self, account_api, accounts):
        """TC-AS-007 PDCA 站点账户返回 registrationEntity=PDCA"""
        acc = accounts["pdca"]
        resp = account_api.get_status(acc["externalAccountId"], acc["registeredEmail"])
        body = assert_success(resp)
        entity = body.get("data", {}).get("registrationEntity")
        assert entity == "PDCA", f"期望 registrationEntity=PDCA，实际={entity}"


class TestAccountStatusAbnormal:
    """异常场景：参数校验与错误处理"""

    def test_missing_external_account_id(self, account_api):
        """TC-AS-101 缺少 externalAccountId，返回 400/422"""
        resp = account_api.get("/v1/account", params={
            "registeredEmail": "jimmy_xuan@leptage.com"
        })
        assert resp.status_code in [400, 422], f"实际 {resp.status_code}"

    def test_missing_registered_email(self, account_api):
        """TC-AS-102 缺少 registeredEmail，返回 400/422"""
        resp = account_api.get("/v1/account", params={
            "externalAccountId": "testjimmmy124321"
        })
        assert resp.status_code in [400, 422], f"实际 {resp.status_code}"

    def test_empty_body(self, account_api):
        """TC-AS-103 空请求参数，返回 400/422"""
        resp = account_api.get("/v1/account", params={})
        assert resp.status_code in [400, 422], f"实际 {resp.status_code}"

    def test_nonexistent_account(self, account_api):
        """TC-AS-104 账户不存在，返回业务错误"""
        resp = account_api.post("/v1/account/status", json={
            "externalAccountId": "nonexistent_account_99999",
            "registeredEmail": "jimmy_xuan@leptage.com",
        })
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != 0, f"不存在账户应返回错误：{body}"

    def test_email_not_match(self, account_api, accounts):
        """TC-AS-105 externalAccountId 与 registeredEmail 不匹配，返回错误"""
        acc = accounts["valid"]
        resp = account_api.post("/v1/account/status", json={
            "externalAccountId": acc["externalAccountId"],
            "registeredEmail": "other_user@leptage.com",
        })
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != 0, f"email 不匹配应返回错误：{body}"

    def test_invalid_email_format(self, account_api, accounts):
        """TC-AS-106 非法 email 格式，返回参数错误"""
        resp = account_api.post("/v1/account/status", json={
            "externalAccountId": accounts["valid"]["externalAccountId"],
            "registeredEmail": "not_an_email",
        })
        assert resp.status_code in [400, 422] or resp.json().get("code") != 0


class TestAccountStatusBoundary:
    """边界场景：特殊字符、超长输入"""

    def test_account_id_max_length(self, account_api):
        """TC-AS-201 超长 externalAccountId（255字符），不应返回 500"""
        resp = account_api.post("/v1/account/status", json={
            "externalAccountId": "a" * 255,
            "registeredEmail": "jimmy_xuan@leptage.com",
        })
        assert resp.status_code != 500, f"超长输入导致服务器错误：{resp.status_code}"

    def test_account_id_special_chars(self, account_api):
        """TC-AS-202 特殊字符 externalAccountId，不应返回 500"""
        resp = account_api.post("/v1/account/status", json={
            "externalAccountId": "test!@#$%^&*()",
            "registeredEmail": "jimmy_xuan@leptage.com",
        })
        assert resp.status_code != 500

    def test_empty_string_account_id(self, account_api):
        """TC-AS-203 空字符串 externalAccountId，返回参数错误"""
        resp = account_api.post("/v1/account/status", json={
            "externalAccountId": "",
            "registeredEmail": "jimmy_xuan@leptage.com",
        })
        assert resp.status_code in [400, 422] or resp.json().get("code") != 0

    def test_email_uppercase(self, account_api, accounts):
        """TC-AS-204 大写 email，验证大小写处理行为（探索性）"""
        acc = accounts["valid"]
        resp = account_api.post("/v1/account/status", json={
            "externalAccountId": acc["externalAccountId"],
            "registeredEmail": acc["registeredEmail"].upper(),
        })
        assert resp.status_code != 500
        print(f"\n大写 email 查询结果：{resp.status_code} - {resp.json()}")


@pytest.mark.security
class TestAccountStatusSecurity:
    """安全场景：SQL 注入、XSS、越权"""

    @pytest.mark.parametrize("injection", [
        "' OR 1=1--",
        "'; DROP TABLE accounts;--",
        "' UNION SELECT * FROM users--",
    ])
    def test_sql_injection_account_id(self, account_api, injection):
        """TC-AS-301 externalAccountId SQL 注入，不应返回 500 或暴露 DB 错误"""
        resp = account_api.post("/v1/account/status", json={
            "externalAccountId": injection,
            "registeredEmail": "jimmy_xuan@leptage.com",
        })
        assert resp.status_code != 500, f"SQL 注入导致服务器错误：{resp.text}"
        assert "SQL" not in resp.text.upper(), f"响应暴露 SQL 错误信息：{resp.text}"

    @pytest.mark.parametrize("xss", [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert(1)>",
        "javascript:alert(1)",
    ])
    def test_xss_account_id(self, account_api, xss):
        """TC-AS-302 XSS payload，不应返回 500"""
        resp = account_api.post("/v1/account/status", json={
            "externalAccountId": xss,
            "registeredEmail": "jimmy_xuan@leptage.com",
        })
        assert resp.status_code != 500

    def test_unauthorized_query(self, account_api, accounts):
        """TC-AS-303 用 A 的 email 查询 B 的账户（越权），应返回错误"""
        acc = accounts["valid"]
        resp = account_api.post("/v1/account/status", json={
            "externalAccountId": "other_user_account_001",
            "registeredEmail": acc["registeredEmail"],
        })
        body = resp.json()
        assert resp.status_code != 200 or body.get("code") != 0, f"不应返回他人账户信息：{body}"


@pytest.mark.performance
class TestAccountStatusPerformance:
    """性能场景：响应时间验证"""

    def test_response_time_single(self, account_api, accounts):
        """TC-AS-401 单次请求响应时间 < 2000ms"""
        acc = accounts["valid"]
        resp = account_api.get_status(acc["externalAccountId"], acc["registeredEmail"])
        assert_response_time(resp, max_ms=2000)

    def test_response_time_consecutive(self, account_api, accounts):
        """TC-AS-402 连续 10 次请求，每次 < 2000ms"""
        acc = accounts["valid"]
        times = []
        for i in range(10):
            resp = account_api.get_status(acc["externalAccountId"], acc["registeredEmail"])
            elapsed = resp.elapsed.total_seconds() * 1000
            times.append(elapsed)
            assert elapsed <= 2000, f"第 {i + 1} 次超时：{elapsed:.0f}ms"
        print(f"\n连续10次：avg={sum(times)/len(times):.0f}ms, max={max(times):.0f}ms")


class TestWalletBalance:
    """查询钱包余额接口测试：GET /v1/wallet/balance"""

    @pytest.mark.smoke
    def test_get_balance_success(self, account_api):
        """TC-BAL-001 正常查询余额"""
        resp = account_api.get_wallet_balance()
        print(f"\n[TC-BAL-001] 响应状态码: {resp.status_code}")
        print(f"[TC-BAL-001] 响应体: {resp.json()}")
        assert_success(resp)

    @pytest.mark.regression
    def test_missing_account_id(self, account_api):
        """TC-BAL-101 缺少 X-ON-BEHALF-OF 请求头，返回错误"""
        resp = account_api.get("/v1/wallet/balance", params={"ccy": "usdt"})
        body = resp.json()
        assert resp.status_code in [400, 401, 422] or body.get("code") != 0

    @pytest.mark.regression
    def test_invalid_ccy(self, account_api):
        """TC-BAL-102 ccy 传入非法值，返回错误码 1000"""
        resp = account_api.get(
            "/v1/wallet/balance",
            headers={"X-ON-BEHALF-OF": "ACC1998628247771996160"},
            params={"ccy": "INVALID_CCY"},
        )
        body = resp.json()
        assert body.get("code") == "1000"
        assert body.get("msg") == "invalid parameter"

    @pytest.mark.regression
    def test_missing_ccy_returns_all_balances(self, account_api):
        """TC-BAL-103 不传 ccy，返回账户下所有币种余额"""
        resp = account_api.get(
            "/v1/wallet/balance",
            headers={"X-ON-BEHALF-OF": "ACC1998628247771996160"},
        )
        print(f"\n[TC-BAL-103] 响应状态码: {resp.status_code}")
        print(f"[TC-BAL-103] 响应体: {resp.json()}")
        assert_success(resp)

    """创建 PDCA 账户接口测试：POST /v1/account/pdca"""

    @pytest.mark.smoke
    def test_create_pdca_success(self, account_api, accounts):
        """TC-PDCA-001 正常创建 PDCA 账户，返回成功
        前置条件：externalAccountId 在系统中不存在
        请求体：externalAccountId（唯一标识）+ registeredEmail（合法邮箱）
        预期结果：HTTP 200，code=0000，data 包含 accountId/userId/status=INACTIVE
        校验点：响应结构符合 CREATE_PDCA_ACCOUNT schema，响应时间 ≤ 2000ms
        """
        external_account_id = f"pdca_{uuid.uuid4().hex[:12]}"
        resp = account_api.create_pdca_account(
            external_account_id,
            accounts["pdca_create"]["registeredEmail"],
        )
        body = assert_success(resp)
        assert_schema(body, account_schema.CREATE_PDCA_ACCOUNT)
        assert_response_time(resp, max_ms=2000)

    @pytest.mark.regression
    def test_create_pdca_duplicate_id(self, account_api, accounts):
        """TC-PDCA-002 重复 externalAccountId，返回 000028
        前置条件：同一 externalAccountId 已成功创建一次
        请求体：与第一次完全相同的 externalAccountId + registeredEmail
        预期结果：HTTP 200，code=000028，msg 包含 'already exist'
        校验点：重复创建不会产生新账户，错误码明确
        """
        external_account_id = f"pdca_{uuid.uuid4().hex[:12]}"
        email = accounts["pdca_create"]["registeredEmail"]
        # 第一次创建成功
        account_api.create_pdca_account(external_account_id, email)
        # 第二次相同 ID 应报错
        resp = account_api.create_pdca_account(external_account_id, email)
        body = resp.json()
        assert body.get("code") == "000028", \
            f"期望错误码 000028，实际：{body}"
        assert "already exist" in body.get("msg", "").lower(), \
            f"期望 msg 包含 'already exist'，实际：{body.get('msg')}"

    @pytest.mark.regression
    def test_create_pdca_missing_account_id(self, account_api, accounts):
        """TC-PDCA-003 缺少 externalAccountId，返回参数错误
        前置条件：无
        请求体：仅包含 registeredEmail，缺少 externalAccountId
        预期结果：HTTP 400 或 422，参数校验失败
        校验点：接口对必填字段做校验，不会创建账户
        """
        resp = account_api.post("/v1/account/pdca", json={
            "registeredEmail": accounts["pdca_create"]["registeredEmail"],
        })
        assert resp.status_code in [400, 422], f"实际 {resp.status_code}"

    @pytest.mark.regression
    def test_create_pdca_missing_email(self, account_api):
        """TC-PDCA-004 缺少 registeredEmail，返回参数错误
        前置条件：无
        请求体：仅包含 externalAccountId，缺少 registeredEmail
        预期结果：HTTP 400 或 422，参数校验失败
        校验点：接口对必填字段做校验，不会创建账户
        """
        resp = account_api.post("/v1/account/pdca", json={
            "externalAccountId": f"pdca_{uuid.uuid4().hex[:12]}",
        })
        assert resp.status_code in [400, 422], f"实际 {resp.status_code}"

    @pytest.mark.regression
    def test_create_pdca_invalid_email(self, account_api):
        """TC-PDCA-005 非法 email 格式，返回参数错误
        前置条件：无
        请求体：externalAccountId 合法，registeredEmail 为非邮箱格式字符串（如 not_an_email）
        预期结果：HTTP 400/422 或 code≠0，邮箱格式校验失败
        校验点：接口对 email 格式做合法性验证
        """
        resp = account_api.post("/v1/account/pdca", json={
            "externalAccountId": f"pdca_{uuid.uuid4().hex[:12]}",
            "registeredEmail": "not_an_email",
        })
        assert resp.status_code in [400, 422] or resp.json().get("code") != 0

    @pytest.mark.regression
    def test_create_pdca_empty_body(self, account_api):
        """TC-PDCA-006 空请求体，返回参数错误"""
        resp = account_api.post("/v1/account/pdca", json={})
        assert resp.status_code in [400, 422], f"实际 {resp.status_code}"


class TestCreatePdcaIndividualAccount:
    """创建 PDCA 个人账户接口测试：POST /v1/account/pdca/individual"""

    @pytest.mark.smoke
    def test_create_pdca_individual_success(self, account_api, accounts):
        """TC-PDCA-IND-001 正常创建 PDCA 个人账户，返回成功
        前置条件：externalAccountId 在系统中不存在
        请求体：externalAccountId + registeredEmail + registrationSource + memberRegistrationSource
        预期结果：HTTP 200，code=0000，data 包含 accountId/userId/status=INACTIVE
        校验点：响应结构符合 CREATE_PDCA_INDIVIDUAL_ACCOUNT schema，响应时间 ≤ 2000ms
        """
        external_account_id = f"pdca_ind_{uuid.uuid4().hex[:12]}"
        resp = account_api.create_pdca_individual_account(
            external_account_id,
            accounts["pdca_create"]["registeredEmail"],
        )
        body = assert_success(resp)
        assert_schema(body, account_schema.CREATE_PDCA_INDIVIDUAL_ACCOUNT)
        assert_response_time(resp, max_ms=2000)

    @pytest.mark.regression
    def test_create_pdca_individual_duplicate_id(self, account_api, accounts):
        """TC-PDCA-IND-002 重复 externalAccountId，返回 000028
        前置条件：同一 externalAccountId 已成功创建一次
        请求体：与第一次完全相同的四个字段
        预期结果：HTTP 200，code=000028，msg 包含 'already exist'
        校验点：重复创建不会产生新账户，错误码明确
        """
        external_account_id = f"pdca_ind_{uuid.uuid4().hex[:12]}"
        email = accounts["pdca_create"]["registeredEmail"]
        account_api.create_pdca_individual_account(external_account_id, email)
        resp = account_api.create_pdca_individual_account(external_account_id, email)
        body = resp.json()
        assert body.get("code") == "000028", \
            f"期望错误码 000028，实际：{body}"
        assert "already exist" in body.get("msg", "").lower(), \
            f"期望 msg 包含 'already exist'，实际：{body.get('msg')}"

    @pytest.mark.regression
    def test_create_pdca_individual_missing_account_id(self, account_api, accounts):
        """TC-PDCA-IND-003 缺少 externalAccountId，返回参数错误
        前置条件：无
        请求体：缺少 externalAccountId，其余字段完整
        预期结果：HTTP 400 或 422，参数校验失败
        校验点：接口对必填字段做校验，不会创建账户
        """
        resp = account_api.post("/v1/account/pdca/individual", json={
            "registeredEmail": accounts["pdca_create"]["registeredEmail"],
            "registrationSource": "PDCA",
            "memberRegistrationSource": "SYKKA",
        })
        assert resp.status_code in [400, 422], f"实际 {resp.status_code}"

    @pytest.mark.regression
    def test_create_pdca_individual_missing_email(self, account_api):
        """TC-PDCA-IND-004 缺少 registeredEmail，返回参数错误
        前置条件：无
        请求体：缺少 registeredEmail，其余字段完整
        预期结果：HTTP 400 或 422，参数校验失败
        校验点：接口对必填字段做校验，不会创建账户
        """
        resp = account_api.post("/v1/account/pdca/individual", json={
            "externalAccountId": f"pdca_ind_{uuid.uuid4().hex[:12]}",
            "registrationSource": "PDCA",
            "memberRegistrationSource": "SYKKA",
        })
        assert resp.status_code in [400, 422], f"实际 {resp.status_code}"

    @pytest.mark.regression
    def test_create_pdca_individual_invalid_email(self, account_api):
        """TC-PDCA-IND-005 非法 email 格式，返回参数错误
        前置条件：无
        请求体：registeredEmail 为非邮箱格式字符串，其余字段完整
        预期结果：HTTP 400/422 或 code≠0，邮箱格式校验失败
        校验点：接口对 email 格式做合法性验证
        """
        resp = account_api.post("/v1/account/pdca/individual", json={
            "externalAccountId": f"pdca_ind_{uuid.uuid4().hex[:12]}",
            "registeredEmail": "not_an_email",
            "registrationSource": "PDCA",
            "memberRegistrationSource": "SYKKA",
        })
        assert resp.status_code in [400, 422] or resp.json().get("code") != 0

    @pytest.mark.regression
    def test_create_pdca_individual_empty_body(self, account_api):
        """TC-PDCA-IND-006 空请求体，返回参数错误"""
        resp = account_api.post("/v1/account/pdca/individual", json={})
        assert resp.status_code in [400, 422], f"实际 {resp.status_code}"

    @pytest.mark.regression
    def test_create_pdca_individual_status_inactive(self, account_api, accounts):
        """TC-PDCA-IND-007 新建账户初始状态应为 INACTIVE
        前置条件：externalAccountId 在系统中不存在
        预期结果：data.status == INACTIVE
        校验点：账户创建后未经激活，状态必须是 INACTIVE
        """
        external_account_id = f"pdca_ind_{uuid.uuid4().hex[:12]}"
        resp = account_api.create_pdca_individual_account(
            external_account_id,
            accounts["pdca_create"]["registeredEmail"],
        )
        body = assert_success(resp)
        status = body.get("data", {}).get("status")
        assert status == "INACTIVE", f"期望 status=INACTIVE，实际={status}"

    @pytest.mark.regression
    def test_create_pdca_individual_default_source_is_sykka(self, account_api, accounts):
        """TC-PDCA-IND-008 不传 memberRegistrationSource 时默认 SYKKA，账户创建成功
        前置条件：无
        请求体：只传 externalAccountId + registeredEmail，不传 memberRegistrationSource
        预期结果：HTTP 200，code=0000，账户正常创建
        校验点：默认值 SYKKA 生效，不影响创建结果
        """
        external_account_id = f"pdca_ind_{uuid.uuid4().hex[:12]}"
        resp = account_api.post("/v1/account/pdca/individual", json={
            "externalAccountId": external_account_id,
            "registeredEmail": accounts["pdca_create"]["registeredEmail"],
            "registrationSource": "PDCA",
        })
        body = assert_success(resp)
        assert_schema(body, account_schema.CREATE_PDCA_INDIVIDUAL_ACCOUNT)

    @pytest.mark.performance
    def test_create_pdca_individual_response_time(self, account_api, accounts):
        """TC-PDCA-IND-009 创建接口响应时间 ≤ 2000ms"""
        external_account_id = f"pdca_ind_{uuid.uuid4().hex[:12]}"
        resp = account_api.create_pdca_individual_account(
            external_account_id,
            accounts["pdca_create"]["registeredEmail"],
        )
        assert_success(resp)
        assert_response_time(resp, max_ms=2000)


class TestUpdateAccountStatus:
    """修改账户状态"""

    @pytest.mark.smoke
    def test_suspend(self, account_api):
        """TC-ACC-STATUS-001 修改账户状态为 SUSPEND"""
        resp = account_api.update_account_status(account_status="SUSPEND")
        print(f"\n[TC-ACC-STATUS-001] 响应状态码: {resp.status_code}")
        print(f"[TC-ACC-STATUS-001] 响应体: {resp.json()}")
        assert_success(resp)

    @pytest.mark.smoke
    def test_active(self, account_api):
        """TC-ACC-STATUS-002 修改账户状态为 Active"""
        resp = account_api.update_account_status(account_status="ACTIVE")
        print(f"\n[TC-ACC-STATUS-002] 响应状态码: {resp.status_code}")
        print(f"[TC-ACC-STATUS-002] 响应体: {resp.json()}")
        assert_success(resp)

    @pytest.mark.regression
    def test_receive_only(self, account_api):
        """TC-ACC-STATUS-003 修改账户状态为 Receive Only"""
        resp = account_api.update_account_status(account_status="RECEIVE_ONLY")
        print(f"\n[TC-ACC-STATUS-003] 响应状态码: {resp.status_code}")
        print(f"[TC-ACC-STATUS-003] 响应体: {resp.json()}")
        assert_success(resp)

    @pytest.mark.skip(reason="WITHDRAW_ONLY 枚举值待确认")
    @pytest.mark.regression
    def test_withdraw_only(self, account_api):
        """TC-ACC-STATUS-004 修改账户状态为 Withdraw Only"""
        resp = account_api.update_account_status(account_status="WITHDRAW_ONLY")
        print(f"\n[TC-ACC-STATUS-004] 响应状态码: {resp.status_code}")
        print(f"[TC-ACC-STATUS-004] 响应体: {resp.json()}")
        assert_success(resp)

    @pytest.mark.regression
    def test_invalid_status(self, account_api):
        """TC-ACC-STATUS-005 非法 accountStatus 值，返回错误"""
        resp = account_api.update_account_status(account_status="INVALID_STATUS")
        body = resp.json()
        assert resp.status_code in [400, 422] or body.get("code") != 0
