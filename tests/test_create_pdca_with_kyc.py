"""
创建 PDCA 账户 + 提交 KYC 基本信息，参数化执行 10 次
运行：TEST_ENV=uat pytest tests/test_create_pdca_with_kyc.py -s -v
"""
import json
import uuid

import allure
import pytest

from api.account_api import AccountAPI
from api.kyc_api import KycAPI
from utils.assertions import assert_success
from utils.data_loader import load_yaml

_ACCOUNTS = load_yaml("accounts.yaml")
_REGISTERED_EMAIL = _ACCOUNTS["pdca_create"]["registeredEmail"]

_EDD = {
    "doneEDD": True,
    "reports": ["20920920920920921"],
    "reportComments": "asdsadasd",
}

_BUSINESS_MODEL = {
    "docs": [],
    "industry": 1,
    "businessDesc": "asdasdw",
    "industryCode": 209,
    "sourceOfFunds": "SELF_HOSTED_WALLET",
    "registryPurpose": "CRYPTOCURRENCY_CONVERT",
    "sourceOfFundsDesc": "asdasdasdsa",
    "companyOnlinePresence": "https://www.baidu.com",
    "needProductionLicense": False,
    "estimatedMonthlyRevenue": "GE_25W_LT_50W",
    "primaryCountryOfOperations": ["HK"],
    "needIndustryQualificationLicense": False,
    "needMedicalDeviceBusinessLicense": False,
}

_INCORPORATE_INFO_BASE = {
    "docs": [
        {"path": ["209209333"], "type": "PROOF_OF_BUSINESS_ADDRESS", "expireDate": "2027-01-01"},
        {"path": ["2092093333"], "type": "INCORPORATION_CERTIFICATE", "expireDate": "2027-01-01"},
        {"path": ["2092093332"], "type": "NNC1_NAR1", "expireDate": "2027-01-01"},
        {"path": ["2092093331"], "type": "BUSINESS_REGISTRATION_CERTIFICATE", "expireDate": "2027-01-01"},
    ],
    "englishName": "xuanhaojun",
    "natureOfBusiness": "",
    "certificateNumber": "asdasdasdasd",
    "incorporationType": "PRIVATE",
    "registeredAddress": {
        "detail": "209", "cityCode": "asd", "postCode": "", "stateCode": "asd",
        "countryCode": "HK", "fullAddress": "hong kong 209",
        "streetLine1": "", "streetLine2": "", "districtCode": "asd",
    },
    "dateOfCommencement": "2001-01-01",
    "incorporationCountry": "HK",
    "registeredEntityName": "xuanhaojun",
    "businessRegistrationNo": "dsadasd232092092",
    "principalPlaceOfBusiness": {
        "detail": "209", "cityCode": "asd", "postCode": "", "stateCode": "asd",
        "countryCode": "HK", "fullAddress": "hong kong 209",
        "streetLine1": "", "streetLine2": "", "districtCode": "asd",
    },
}


def _build_kyc_payload(run_id: str) -> dict:
    """每次调用生成唯一 vendorId，避免重复报错"""
    ubos = [
        {
            "idDocs": [
                {"path": ["asdsadasd"], "type": "DRIVERS_LICENSE_FRONT", "idNumber": "20920920920912", "expireDate": "2027-01-01"},
                {"path": ["asdadsasd"], "type": "DRIVERS_LICENSE_BACK", "idNumber": "20920933124321121", "expireDate": "2027-01-01"},
            ],
            "shares": "25",
            "contact": {"email": "", "phone": {"number": "12312312", "countryCode": "+852"}},
            "lastName": "ubos",
            "firstName": "ubos",
            "idAddress": {
                "detail": "209", "cityCode": "asd", "postCode": "", "stateCode": "asd",
                "countryCode": "HK", "fullAddress": "hong kong 209",
                "streetLine1": "", "streetLine2": "", "districtCode": "asd",
            },
            "lastNameEn": "ubos",
            "dateOfBirth": "2001-01-01",
            "firstNameEn": "ubos",
            "nationality": "HK",
            "amlScreenings": [
                {"name": "asd", "result": "OTHER_ACCEPT", "status": "PASS", "comment": "209",
                 "vendorId": f"ubo_{run_id}_1", "screeningType": "UBO"},
                {"name": "asd", "result": "NONE_OF_ABOVE", "status": "PASS", "comment": "209",
                 "vendorId": f"ubo_{run_id}_2", "screeningType": "UBO"},
            ],
            "residentialAddress": {
                "detail": "209", "cityCode": "asd", "postCode": "", "stateCode": "asd",
                "countryCode": "HK", "fullAddress": "hong kong 209",
                "streetLine1": "", "streetLine2": "", "districtCode": "asd",
            },
            "residentialAddressIsIdAddress": True,
        }
    ]

    directors = [
        {
            "idDocs": [
                {"path": ["asdsadasd"], "type": "PASSPORT", "idNumber": "20920920920912", "expireDate": "2027-01-01"},
            ],
            "shares": "25",
            "contact": {"email": "", "phone": {"number": "12312312", "countryCode": "+852"}},
            "lastName": "directors",
            "firstName": "directors",
            "idAddress": {
                "detail": "209", "cityCode": "asd", "postCode": "", "stateCode": "asd",
                "countryCode": "HK", "fullAddress": "hong kong 209",
                "streetLine1": "", "streetLine2": "", "districtCode": "asd",
            },
            "lastNameEn": "directors",
            "dateOfBirth": "2001-01-01",
            "firstNameEn": "directors",
            "nationality": "HK",
            "amlScreenings": [
                {"name": "asd", "result": "OTHER_ACCEPT", "status": "PASS", "comment": "209",
                 "vendorId": f"dir_{run_id}_1", "screeningType": "DIRECTOR"},
                {"name": "asd", "result": "NONE_OF_ABOVE", "status": "PASS", "comment": "209",
                 "vendorId": f"dir_{run_id}_2", "screeningType": "DIRECTOR"},
            ],
            "residentialAddress": {
                "detail": "209", "cityCode": "asd", "postCode": "", "stateCode": "asd",
                "countryCode": "HK", "fullAddress": "hong kong 209",
                "streetLine1": "", "streetLine2": "", "districtCode": "asd",
            },
            "residentialAddressIsIdAddress": True,
        }
    ]

    incorporate_info = {
        **_INCORPORATE_INFO_BASE,
        "amlScreenings": [
            {"name": "asd", "result": "NONE_OF_ABOVE", "status": "PASS", "comment": "209",
             "vendorId": f"company_{run_id}_1", "screeningType": "COMPANY"},
            {"name": "asd", "result": "NONE_OF_ABOVE", "status": "PASS", "comment": "209",
             "vendorId": f"company_{run_id}_2", "screeningType": "COMPANY_EN"},
            {"name": "asd", "result": "NONE_OF_ABOVE", "status": "PASS", "comment": "209",
             "vendorId": f"company_{run_id}_3", "screeningType": "COMPANY_EN"},
        ],
    }

    return dict(
        edd=_EDD,
        ubos=ubos,
        directors=directors,
        business_model=_BUSINESS_MODEL,
        incorporate_info=incorporate_info,
        registration_source="PARTNER_REFERRAL",
    )


@allure.feature("PDCA 账户 + KYC")
class TestCreatePdcaWithKyc:
    """每次独立创建 PDCA 账户并提交 KYC 基本信息，执行 5 次"""

    @allure.story("创建 PDCA 账户 + 提交 KYC")
    @pytest.mark.parametrize("run_index", range(10), ids=[f"第{i + 1}次" for i in range(10)])
    def test_create_pdca_and_kyc(self, run_index):
        account_api = AccountAPI(role="merchant")
        kyc_api = KycAPI(role="merchant")
        try:
            external_account_id = f"pdca_{uuid.uuid4().hex[:12]}"
            run_id = uuid.uuid4().hex[:8]
            allure.dynamic.title(f"第{run_index + 1}次 创建PDCA账户并提交KYC [{external_account_id}]")

            with allure.step(f"创建 PDCA 账户 [{external_account_id}]"):
                create_resp = account_api.create_pdca_account(external_account_id, _REGISTERED_EMAIL)
                allure.attach(
                    json.dumps(create_resp.json(), ensure_ascii=False, indent=2),
                    name="创建账户响应",
                    attachment_type=allure.attachment_type.JSON,
                )
                body = assert_success(create_resp)
                account_id = body["data"]["accountId"]
                print(f"\n[第{run_index + 1}次] PDCA账户创建成功: externalId={external_account_id}, accountId={account_id}")

            with allure.step(f"提交 KYC 基本信息 [accountId={account_id}]"):
                kyc_resp = kyc_api.create_kyc_basic(
                    account_id=account_id,
                    **_build_kyc_payload(run_id),
                )
                allure.attach(
                    json.dumps(kyc_resp.json(), ensure_ascii=False, indent=2),
                    name="KYC 响应",
                    attachment_type=allure.attachment_type.JSON,
                )
                assert_success(kyc_resp)
                print(f"[第{run_index + 1}次] KYC 提交成功: accountId={account_id}")
        finally:
            account_api.close()
            kyc_api.close()
