"""
法币收款人接口测试
接口：POST /v2/beneficiary/create

请求参数：
{
  "currencies": ["USD"],
  "bankLocation": "HK",
  "accountNickName": "nick...",
  "beneficiaryType": "SN",
  "accountType": "BUSINESS",
  "beneficiaryName": "...",
  "bankSwiftCode": "ABFLHKHH",
  "bankName": "testbank",
  "bankAccountNumber": "...",
  "countryDialCode": "+852",
  "contactPhone": "98765432",
  "recipientLocation": "HK",
  "recipientProvince": "Tai Po District",
  "street1": "teststreet1"
}
"""
import time
import uuid

import pytest

from utils.assertions import assert_success, assert_response_time

ACCOUNT_ID = "ACC1996532313185505280"


def _nick():
    return f"nick{uuid.uuid4().hex[:12]}"


def _base_payload(**overrides):
    payload = dict(
        account_id=ACCOUNT_ID,
        currencies=["USD"],
        bank_location="HK",
        account_nick_name=_nick(),
        beneficiary_type="SN",
        account_type="BUSINESS",
        beneficiary_name="hans",
        bank_swift_code="ABFLHKHH",
        bank_name="testbank",
        bank_account_number="4220250507133538",
        country_dial_code="+852",
        contact_phone="98765432",
        recipient_location="HK",
        recipient_province="Tai Po District",
        street1="teststreet1",
    )
    payload.update(overrides)
    return payload


class TestCreateBeneficiaryV2Normal:
    """正常场景 POST /v2/beneficiary/create"""

    @pytest.mark.smoke
    def test_create_beneficiary_v2_success(self, beneficiary_api):
        """TC-BENE-V2-001 创建法币收款人，返回成功
        预期结果：HTTP 200，code=0000，data 包含 beneId
        """
        resp = beneficiary_api.create_beneficiary_v2(**_base_payload())
        print(f"\n[TC-BENE-V2-001] {resp.status_code} {resp.json()}")
        body = assert_success(resp)
        assert body.get("data") is not None, f"data 不应为空：{body}"

    @pytest.mark.regression
    def test_create_beneficiary_v2_bene_id_not_empty(self, beneficiary_api):
        """TC-BENE-V2-002 返回的 beneId 不为空"""
        resp = beneficiary_api.create_beneficiary_v2(**_base_payload())
        data = assert_success(resp).get("data", {})
        assert data.get("beneId"), f"beneId 不应为空：{data}"

    @pytest.mark.regression
    def test_create_beneficiary_v2_nick_unique(self, beneficiary_api):
        """TC-BENE-V2-003 不同 accountNickName 可重复创建"""
        resp1 = beneficiary_api.create_beneficiary_v2(**_base_payload())
        resp2 = beneficiary_api.create_beneficiary_v2(**_base_payload())
        assert_success(resp1)
        assert_success(resp2)

    @pytest.mark.regression
    def test_create_beneficiary_v2_with_iban(self, beneficiary_api):
        """TC-BENE-V2-004 使用 IBAN 创建收款人"""
        resp = beneficiary_api.create_beneficiary_v2(**_base_payload(
            bank_location="ES",
            bank_swift_code="DBSCESMM",
            bank_name="DEUTSCHE BANK AG SPANISH BRANCH",
            bank_account_number=None,
            iban="ES0414650120311760423470",
            country_dial_code="+372",
            contact_phone="12345678909",
            recipient_location="ES",
            recipient_province="Burgos",
            street1="fsqgeqr",
        ))
        print(f"\n[TC-BENE-V2-004] {resp.status_code} {resp.json()}")
        assert_success(resp)

    @pytest.mark.regression
    def test_create_beneficiary_v2_response_time(self, beneficiary_api):
        """TC-BENE-V2-005 接口响应时间在 3000ms 以内"""
        resp = beneficiary_api.create_beneficiary_v2(**_base_payload())
        assert_success(resp)
        assert_response_time(resp, max_ms=3000)


class TestCreateBeneficiaryV2Abnormal:
    """异常场景 POST /v2/beneficiary/create"""

    @pytest.mark.regression
    def test_create_beneficiary_v2_missing_currencies(self, beneficiary_api):
        """TC-BENE-V2-101 缺少 currencies，返回 400"""
        resp = beneficiary_api.post(
            "/v2/beneficiary/create",
            headers={"X-ON-BEHALF-OF": ACCOUNT_ID},
            json={
                "bankLocation": "HK",
                "accountNickName": _nick(),
                "beneficiaryType": "SN",
                "accountType": "BUSINESS",
                "beneficiaryName": "hans",
                "bankSwiftCode": "ABFLHKHH",
                "bankName": "testbank",
                "bankAccountNumber": "4220250507133538",
            },
        )
        print(f"\n[TC-BENE-V2-101] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"缺少 currencies 应返回 400，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_create_beneficiary_v2_missing_bank_location(self, beneficiary_api):
        """TC-BENE-V2-102 缺少 bankLocation，返回 400"""
        resp = beneficiary_api.post(
            "/v2/beneficiary/create",
            headers={"X-ON-BEHALF-OF": ACCOUNT_ID},
            json={
                "currencies": ["USD"],
                "accountNickName": _nick(),
                "beneficiaryType": "SN",
                "accountType": "BUSINESS",
                "beneficiaryName": "hans",
                "bankSwiftCode": "ABFLHKHH",
                "bankName": "testbank",
                "bankAccountNumber": "4220250507133538",
            },
        )
        print(f"\n[TC-BENE-V2-102] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"缺少 bankLocation 应返回 400，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_create_beneficiary_v2_missing_beneficiary_name(self, beneficiary_api):
        """TC-BENE-V2-103 缺少 beneficiaryName，返回 400"""
        resp = beneficiary_api.post(
            "/v2/beneficiary/create",
            headers={"X-ON-BEHALF-OF": ACCOUNT_ID},
            json={
                "currencies": ["USD"],
                "bankLocation": "HK",
                "accountNickName": _nick(),
                "beneficiaryType": "SN",
                "accountType": "BUSINESS",
                "bankSwiftCode": "ABFLHKHH",
                "bankName": "testbank",
                "bankAccountNumber": "4220250507133538",
            },
        )
        print(f"\n[TC-BENE-V2-103] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"缺少 beneficiaryName 应返回 400，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_create_beneficiary_v2_both_iban_and_account_number(self, beneficiary_api):
        """TC-BENE-V2-104 同时传 iban 和 bankAccountNumber，返回 400
        预期结果：code=1000，msg 提示不能同时填写
        """
        resp = beneficiary_api.create_beneficiary_v2(**_base_payload(
            iban="DK20250507133538",
        ))
        print(f"\n[TC-BENE-V2-104] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"同时填 iban 和 bankAccountNumber 应返回 400，实际：{resp.status_code}"
        assert "iban" in resp.json().get("msg", "").lower() or \
               "account" in resp.json().get("msg", "").lower(), \
            f"错误信息应提示冲突字段：{resp.json()}"

    @pytest.mark.regression
    def test_create_beneficiary_v2_invalid_beneficiary_type(self, beneficiary_api):
        """TC-BENE-V2-105 beneficiaryType 传入非法值，返回 400"""
        resp = beneficiary_api.create_beneficiary_v2(**_base_payload(
            beneficiary_type="INVALID_TYPE",
        ))
        print(f"\n[TC-BENE-V2-105] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"非法 beneficiaryType 应返回 400，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_create_beneficiary_v2_invalid_iban_format(self, beneficiary_api):
        """TC-BENE-V2-106 iban 格式错误，返回 400"""
        resp = beneficiary_api.create_beneficiary_v2(**_base_payload(
            bank_account_number=None,
            iban="INVALID_IBAN_FORMAT",
        ))
        print(f"\n[TC-BENE-V2-106] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"IBAN 格式错误应返回 400，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_create_beneficiary_v2_missing_account_id(self, beneficiary_api):
        """TC-BENE-V2-107 缺少 X-ON-BEHALF-OF header，返回 4xx"""
        resp = beneficiary_api.post(
            "/v2/beneficiary/create",
            json={
                "currencies": ["USD"],
                "bankLocation": "HK",
                "accountNickName": _nick(),
                "beneficiaryType": "SN",
                "accountType": "BUSINESS",
                "beneficiaryName": "hans",
                "bankSwiftCode": "ABFLHKHH",
                "bankName": "testbank",
                "bankAccountNumber": "4220250507133538",
            },
        )
        print(f"\n[TC-BENE-V2-107] {resp.status_code} {resp.json()}")
        assert resp.status_code in [400, 401, 403], \
            f"缺少账户 ID 应返回 4xx，实际：{resp.status_code}"

    @pytest.mark.regression
    def test_create_beneficiary_v2_invalid_swift_code(self, beneficiary_api):
        """TC-BENE-V2-108 bankSwiftCode 格式非法，返回 400"""
        resp = beneficiary_api.create_beneficiary_v2(**_base_payload(
            bank_swift_code="INVALID",
        ))
        print(f"\n[TC-BENE-V2-108] {resp.status_code} {resp.json()}")
        assert resp.status_code == 400, \
            f"非法 SWIFT code 应返回 400，实际：{resp.status_code}"
