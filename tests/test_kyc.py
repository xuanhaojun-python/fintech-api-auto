"""
KYC 接口测试
覆盖：创建账户 KYC 基本信息
"""
import json
import uuid

import allure
import pytest

from utils.assertions import assert_success

_RUN_ID = uuid.uuid4().hex[:8]

_EDD = {
    "doneEDD": True,
    "reports": ["20920920920920921"],
    "reportComments": "asdsadasd",
}

_UBOS = [
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
             "vendorId": f"ubo test {_RUN_ID}", "screeningType": "UBO"},
            {"name": "asd", "result": "NONE_OF_ABOVE", "status": "PASS", "comment": "209",
             "vendorId": f"ubo1 test {_RUN_ID}", "screeningType": "UBO"},
        ],
        "residentialAddress": {
            "detail": "209", "cityCode": "asd", "postCode": "", "stateCode": "asd",
            "countryCode": "HK", "fullAddress": "hong kong 209",
            "streetLine1": "", "streetLine2": "", "districtCode": "asd",
        },
        "residentialAddressIsIdAddress": True,
    }
]

_DIRECTORS = [
    {
        "idDocs": [
            {"path": ["asdsadasd"], "type": "PERMANENT_RESIDENT_CARD_FRONT", "idNumber": "20920920920912", "expireDate": "2027-01-01"},
            {"path": ["asdadsasd"], "type": "PERMANENT_RESIDENT_CARD_BACK", "idNumber": "2092093121", "expireDate": "2027-01-01"},
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
             "vendorId": f"directors test {_RUN_ID}", "screeningType": "DIRECTOR"},
            {"name": "asd", "result": "NONE_OF_ABOVE", "status": "PASS", "comment": "209",
             "vendorId": f"directors1 test {_RUN_ID}", "screeningType": "DIRECTOR"},
        ],
        "residentialAddress": {
            "detail": "209", "cityCode": "asd", "postCode": "", "stateCode": "asd",
            "countryCode": "HK", "fullAddress": "hong kong 209",
            "streetLine1": "", "streetLine2": "", "districtCode": "asd",
        },
        "residentialAddressIsIdAddress": True,
    }
]

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

_INCORPORATE_INFO = {
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
    "amlScreenings": [
        {"name": "asd", "result": "NONE_OF_ABOVE", "status": "PASS", "comment": "209",
         "vendorId": f"company test {_RUN_ID}", "screeningType": "COMPANY"},
        {"name": "asd", "result": "NONE_OF_ABOVE", "status": "PASS", "comment": "209",
         "vendorId": f"company en test {_RUN_ID}", "screeningType": "COMPANY_EN"},
        {"name": "asd", "result": "NONE_OF_ABOVE", "status": "PASS", "comment": "209",
         "vendorId": f"company en 1 test {_RUN_ID}", "screeningType": "COMPANY_EN"},
    ],
}


@allure.feature("KYC")
class TestCreateKycBasic:
    """创建账户 KYC 基本信息"""

    @allure.story("提交 KYC 基本信息")
    @allure.title("TC-KYC-001 正常提交 KYC 基本信息")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_create_kyc_basic(self, kyc_api, pdca_account_id):
        """TC-KYC-001 正常提交 KYC 基本信息"""
        allure.dynamic.description(f"使用账户 {pdca_account_id} 提交完整 KYC 信息")

        with allure.step("提交 KYC 基本信息"):
            resp = kyc_api.create_kyc_basic(
                account_id=pdca_account_id,
                edd=_EDD,
                ubos=_UBOS,
                agent=None,
                directors=_DIRECTORS,
                business_model=_BUSINESS_MODEL,
                incorporate_info=_INCORPORATE_INFO,
                registration_source="PARTNER_REFERRAL",
            )

        allure.attach(
            json.dumps(resp.request.body if hasattr(resp.request, "body") else {}, ensure_ascii=False, indent=2),
            name="请求体",
            attachment_type=allure.attachment_type.JSON,
        )
        allure.attach(
            json.dumps(resp.json(), ensure_ascii=False, indent=2),
            name="响应体",
            attachment_type=allure.attachment_type.JSON,
        )
        allure.attach(
            str(resp.status_code),
            name="响应状态码",
            attachment_type=allure.attachment_type.TEXT,
        )

        with allure.step("验证响应成功"):
            assert_success(resp)


@allure.feature("KYC")
class TestSaveIndividualKyc:
    """保存个人 KYC 基本信息：PUT /v1/kyc/individual/basic/save"""

    @allure.story("保存个人 KYC 基本信息")
    @allure.title("TC-KYC-IND-001 正常保存个人 KYC 基本信息")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_save_individual_kyc_success(self, kyc_api, pdca_individual_account_id):
        """TC-KYC-IND-001 正常保存个人 KYC 基本信息
        前置条件：已创建 PDCA 个人账户
        请求体：fullName + fullNameEn + dateOfBirth + nationality + countryOfResidence
        预期结果：HTTP 200，code=0000
        """
        with allure.step("保存个人 KYC 基本信息"):
            resp = kyc_api.save_individual_kyc(
                account_id=pdca_individual_account_id,
                full_name="xuanhaojun",
                full_name_en="xuan  SIT",
                date_of_birth="2000-05-15",
                nationality="US",
                country_of_residence="HK",
            )

        allure.attach(
            json.dumps(resp.json(), ensure_ascii=False, indent=2),
            name="响应体",
            attachment_type=allure.attachment_type.JSON,
        )
        allure.attach(
            str(resp.status_code),
            name="响应状态码",
            attachment_type=allure.attachment_type.TEXT,
        )

        with allure.step("验证响应成功"):
            assert_success(resp)

    @allure.story("保存个人 KYC 基本信息")
    @allure.title("TC-KYC-IND-002 缺少 fullName，返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_save_individual_kyc_missing_full_name(self, kyc_api, pdca_individual_account_id):
        """TC-KYC-IND-002 缺少 fullName，返回参数错误
        前置条件：已创建 PDCA 个人账户
        请求体：缺少 fullName，其余字段完整
        预期结果：HTTP 400 或 422，参数校验失败
        """
        with allure.step("发送缺少 fullName 的请求"):
            resp = kyc_api.put("/v1/kyc/individual/basic/save",
                               headers={"X-ON-BEHALF-OF": pdca_individual_account_id},
                               json={
                                   "fullNameEn": "xuan  SIT",
                                   "dateOfBirth": "2000-05-15",
                                   "nationality": "US",
                                   "countryOfResidence": "HK",
                               })
        with allure.step("验证返回参数错误"):
            assert resp.status_code in [400, 422], f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("保存个人 KYC 基本信息")
    @allure.title("TC-KYC-IND-003 缺少 dateOfBirth，返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_save_individual_kyc_missing_date_of_birth(self, kyc_api, pdca_individual_account_id):
        """TC-KYC-IND-003 缺少 dateOfBirth，返回参数错误
        前置条件：已创建 PDCA 个人账户
        请求体：缺少 dateOfBirth，其余字段完整
        预期结果：HTTP 400 或 422，参数校验失败
        """
        with allure.step("发送缺少 dateOfBirth 的请求"):
            resp = kyc_api.put("/v1/kyc/individual/basic/save",
                               headers={"X-ON-BEHALF-OF": pdca_individual_account_id},
                               json={
                                   "fullName": "xuanhaojun",
                                   "fullNameEn": "xuan  SIT",
                                   "nationality": "US",
                                   "countryOfResidence": "HK",
                               })
        with allure.step("验证返回参数错误"):
            assert resp.status_code in [400, 422], f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("保存个人 KYC 基本信息")
    @allure.title("TC-KYC-IND-004 dateOfBirth 格式非法，返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_save_individual_kyc_invalid_date_of_birth(self, kyc_api, pdca_individual_account_id):
        """TC-KYC-IND-004 dateOfBirth 格式非法，返回参数错误
        前置条件：已创建 PDCA 个人账户
        请求体：dateOfBirth 传入非日期格式字符串
        预期结果：HTTP 400/422 或 code≠0000
        """
        with allure.step("发送非法 dateOfBirth 请求"):
            resp = kyc_api.put("/v1/kyc/individual/basic/save",
                               headers={"X-ON-BEHALF-OF": pdca_individual_account_id},
                               json={
                                   "fullName": "xuanhaojun",
                                   "fullNameEn": "xuan  SIT",
                                   "dateOfBirth": "not-a-date",
                                   "nationality": "US",
                                   "countryOfResidence": "HK",
                               })
        with allure.step("验证返回参数错误"):
            assert resp.status_code in [400, 422] or resp.json().get("code") != "0000", \
                f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("保存个人 KYC 基本信息")
    @allure.title("TC-KYC-IND-005 缺少 X-ON-BEHALF-OF header，返回未授权")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_save_individual_kyc_missing_account_header(self, kyc_api):
        """TC-KYC-IND-005 缺少 X-ON-BEHALF-OF header，返回未授权
        前置条件：无
        请求体：完整字段，但不传 X-ON-BEHALF-OF header
        预期结果：HTTP 400 或 401/403
        """
        with allure.step("发送缺少账户 header 的请求"):
            resp = kyc_api.put("/v1/kyc/individual/basic/save",
                               json={
                                   "fullName": "xuanhaojun",
                                   "fullNameEn": "xuan  SIT",
                                   "dateOfBirth": "2000-05-15",
                                   "nationality": "US",
                                   "countryOfResidence": "HK",
                               })
        with allure.step("验证返回未授权"):
            assert resp.status_code in [400, 401, 403], f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("保存个人 KYC 基本信息")
    @allure.title("TC-KYC-IND-006 空请求体，返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_save_individual_kyc_empty_body(self, kyc_api, pdca_individual_account_id):
        """TC-KYC-IND-006 空请求体，返回参数错误
        前置条件：已创建 PDCA 个人账户
        请求体：{}
        预期结果：HTTP 400 或 422
        """
        with allure.step("发送空请求体"):
            resp = kyc_api.put("/v1/kyc/individual/basic/save",
                               headers={"X-ON-BEHALF-OF": pdca_individual_account_id},
                               json={})
        with allure.step("验证返回参数错误"):
            assert resp.status_code in [400, 422], f"实际 {resp.status_code}，响应：{resp.json()}"


@allure.feature("KYC")
class TestGetKycResult:
        """TC-KYC-101 正常查询 KYC 审核结果"""
        allure.dynamic.description(f"查询账户 {pdca_account_id} 的 KYC 审核结果")

        with allure.step("查询 KYC 审核结果"):
            resp = kyc_api.get_kyc_result(account_id=pdca_account_id)

        allure.attach(
            json.dumps(resp.json(), ensure_ascii=False, indent=2),
            name="响应体",
            attachment_type=allure.attachment_type.JSON,
        )
        allure.attach(
            str(resp.status_code),
            name="响应状态码",
            attachment_type=allure.attachment_type.TEXT,
        )

        with allure.step("验证响应成功"):
            assert_success(resp)

        with allure.step("记录审核结果"):
            data = resp.json().get("data", {})
            allure.attach(
                json.dumps(data, ensure_ascii=False, indent=2),
                name="KYC 审核详情",
                attachment_type=allure.attachment_type.JSON,
            )
