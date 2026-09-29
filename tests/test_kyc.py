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
    """创建账户 KYC 基本信息：POST /v1/kyc/basic"""

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

    @allure.story("提交 KYC 基本信息")
    @allure.title("TC-KYC-002 缺少 incorporateInfo，返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_create_kyc_basic_missing_incorporate_info(self, kyc_api, pdca_account_id):
        """TC-KYC-002 缺少 incorporateInfo，返回参数错误
        前置条件：已创建 PDCA 企业账户
        请求体：缺少 incorporateInfo，其余字段完整
        预期结果：HTTP 400/422 或 code≠0000
        """
        with allure.step("发送缺少 incorporateInfo 的请求"):
            resp = kyc_api.create_kyc_basic(
                account_id=pdca_account_id,
                edd=_EDD,
                ubos=_UBOS,
                directors=_DIRECTORS,
                business_model=_BUSINESS_MODEL,
                registration_source="PARTNER_REFERRAL",
            )
        with allure.step("验证返回参数错误"):
            assert resp.status_code in [400, 422] or resp.json().get("code") != "0000", \
                f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("提交 KYC 基本信息")
    @allure.title("TC-KYC-003 缺少 businessModel，返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_create_kyc_basic_missing_business_model(self, kyc_api, pdca_account_id):
        """TC-KYC-003 缺少 businessModel，返回参数错误
        前置条件：已创建 PDCA 企业账户
        请求体：缺少 businessModel，其余字段完整
        预期结果：HTTP 400/422 或 code≠0000
        """
        with allure.step("发送缺少 businessModel 的请求"):
            resp = kyc_api.create_kyc_basic(
                account_id=pdca_account_id,
                edd=_EDD,
                ubos=_UBOS,
                directors=_DIRECTORS,
                incorporate_info=_INCORPORATE_INFO,
                registration_source="PARTNER_REFERRAL",
            )
        with allure.step("验证返回参数错误"):
            assert resp.status_code in [400, 422] or resp.json().get("code") != "0000", \
                f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("提交 KYC 基本信息")
    @allure.title("TC-KYC-004 缺少 ubos，返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_create_kyc_basic_missing_ubos(self, kyc_api, pdca_account_id):
        """TC-KYC-004 缺少 ubos，返回参数错误
        前置条件：已创建 PDCA 企业账户
        请求体：缺少 ubos，其余字段完整
        预期结果：HTTP 400/422 或 code≠0000
        """
        with allure.step("发送缺少 ubos 的请求"):
            resp = kyc_api.create_kyc_basic(
                account_id=pdca_account_id,
                edd=_EDD,
                directors=_DIRECTORS,
                business_model=_BUSINESS_MODEL,
                incorporate_info=_INCORPORATE_INFO,
                registration_source="PARTNER_REFERRAL",
            )
        with allure.step("验证返回参数错误"):
            assert resp.status_code in [400, 422] or resp.json().get("code") != "0000", \
                f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("提交 KYC 基本信息")
    @allure.title("TC-KYC-005 缺少 directors，返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_create_kyc_basic_missing_directors(self, kyc_api, pdca_account_id):
        """TC-KYC-005 缺少 directors，返回参数错误
        前置条件：已创建 PDCA 企业账户
        请求体：缺少 directors，其余字段完整
        预期结果：HTTP 400/422 或 code≠0000
        """
        with allure.step("发送缺少 directors 的请求"):
            resp = kyc_api.create_kyc_basic(
                account_id=pdca_account_id,
                edd=_EDD,
                ubos=_UBOS,
                business_model=_BUSINESS_MODEL,
                incorporate_info=_INCORPORATE_INFO,
                registration_source="PARTNER_REFERRAL",
            )
        with allure.step("验证返回参数错误"):
            assert resp.status_code in [400, 422] or resp.json().get("code") != "0000", \
                f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("提交 KYC 基本信息")
    @allure.title("TC-KYC-006 无效 accountId，返回未授权或账户不存在")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_create_kyc_basic_invalid_account(self, kyc_api):
        """TC-KYC-006 无效 accountId，返回未授权或账户不存在
        前置条件：无
        请求体：完整字段，X-ON-BEHALF-OF 传入不存在的 accountId
        预期结果：HTTP 400/401/403/404
        """
        with allure.step("发送无效 accountId 请求"):
            resp = kyc_api.create_kyc_basic(
                account_id="invalid_account_id_000",
                edd=_EDD,
                ubos=_UBOS,
                directors=_DIRECTORS,
                business_model=_BUSINESS_MODEL,
                incorporate_info=_INCORPORATE_INFO,
                registration_source="PARTNER_REFERRAL",
            )
        with allure.step("验证返回错误"):
            assert resp.status_code in [400, 401, 403, 404] or resp.json().get("code") != "0000", \
                f"实际 {resp.status_code}，响应：{resp.json()}"


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

    @allure.story("保存个人 KYC 基本信息")
    @allure.title("TC-KYC-IND-007 缺少 nationality，返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_save_individual_kyc_missing_nationality(self, kyc_api, pdca_individual_account_id):
        """TC-KYC-IND-007 缺少 nationality，返回参数错误
        前置条件：已创建 PDCA 个人账户
        请求体：缺少 nationality，其余字段完整
        预期结果：HTTP 400/422 或 code≠0000
        """
        with allure.step("发送缺少 nationality 的请求"):
            resp = kyc_api.put("/v1/kyc/individual/basic/save",
                               headers={"X-ON-BEHALF-OF": pdca_individual_account_id},
                               json={
                                   "fullName": "xuanhaojun",
                                   "fullNameEn": "xuan  SIT",
                                   "dateOfBirth": "2000-05-15",
                                   "countryOfResidence": "HK",
                               })
        with allure.step("验证返回参数错误"):
            assert resp.status_code in [400, 422] or resp.json().get("code") != "0000", \
                f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("保存个人 KYC 基本信息")
    @allure.title("TC-KYC-IND-008 缺少 countryOfResidence，返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_save_individual_kyc_missing_country_of_residence(self, kyc_api, pdca_individual_account_id):
        """TC-KYC-IND-008 缺少 countryOfResidence，返回参数错误
        前置条件：已创建 PDCA 个人账户
        请求体：缺少 countryOfResidence，其余字段完整
        预期结果：HTTP 400/422 或 code≠0000
        """
        with allure.step("发送缺少 countryOfResidence 的请求"):
            resp = kyc_api.put("/v1/kyc/individual/basic/save",
                               headers={"X-ON-BEHALF-OF": pdca_individual_account_id},
                               json={
                                   "fullName": "xuanhaojun",
                                   "fullNameEn": "xuan  SIT",
                                   "dateOfBirth": "2000-05-15",
                                   "nationality": "US",
                               })
        with allure.step("验证返回参数错误"):
            assert resp.status_code in [400, 422] or resp.json().get("code") != "0000", \
                f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("保存个人 KYC 基本信息")
    @allure.title("TC-KYC-IND-009 nationality 格式非法（非2位国家码），返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_save_individual_kyc_invalid_nationality(self, kyc_api, pdca_individual_account_id):
        """TC-KYC-IND-009 nationality 格式非法（非2位国家码），返回参数错误
        前置条件：已创建 PDCA 个人账户
        请求体：nationality 传入非2位国家码 "INVALID"
        预期结果：HTTP 400/422 或 code≠0000
        """
        with allure.step("发送非法 nationality 请求"):
            resp = kyc_api.put("/v1/kyc/individual/basic/save",
                               headers={"X-ON-BEHALF-OF": pdca_individual_account_id},
                               json={
                                   "fullName": "xuanhaojun",
                                   "fullNameEn": "xuan  SIT",
                                   "dateOfBirth": "2000-05-15",
                                   "nationality": "INVALID",
                                   "countryOfResidence": "HK",
                               })
        with allure.step("验证返回参数错误"):
            assert resp.status_code in [400, 422] or resp.json().get("code") != "0000", \
                f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("保存个人 KYC 基本信息")
    @allure.title("TC-KYC-IND-010 dateOfBirth 为未来日期，返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_save_individual_kyc_future_date_of_birth(self, kyc_api, pdca_individual_account_id):
        """TC-KYC-IND-010 dateOfBirth 为未来日期，返回参数错误
        前置条件：已创建 PDCA 个人账户
        请求体：dateOfBirth 传入未来日期 "2099-01-01"
        预期结果：HTTP 400/422 或 code≠0000
        """
        with allure.step("发送未来 dateOfBirth 请求"):
            resp = kyc_api.put("/v1/kyc/individual/basic/save",
                               headers={"X-ON-BEHALF-OF": pdca_individual_account_id},
                               json={
                                   "fullName": "xuanhaojun",
                                   "fullNameEn": "xuan  SIT",
                                   "dateOfBirth": "2099-01-01",
                                   "nationality": "US",
                                   "countryOfResidence": "HK",
                               })
        with allure.step("验证返回参数错误"):
            assert resp.status_code in [400, 422] or resp.json().get("code") != "0000", \
                f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("保存个人 KYC 基本信息")
    @allure.title("TC-KYC-IND-011 携带可选字段（gender、sourceOfWealth）正常保存")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_save_individual_kyc_with_optional_fields(self, kyc_api, pdca_individual_account_id):
        """TC-KYC-IND-011 携带可选字段（gender、sourceOfWealth）正常保存
        前置条件：已创建 PDCA 个人账户
        请求体：必填字段 + gender=MALE + sourceOfWealth=SALARY
        预期结果：HTTP 200，code=0000
        """
        with allure.step("保存携带可选字段的个人 KYC"):
            resp = kyc_api.save_individual_kyc(
                account_id=pdca_individual_account_id,
                full_name="xuanhaojun",
                full_name_en="xuan  SIT",
                date_of_birth="2000-05-15",
                nationality="US",
                country_of_residence="HK",
                gender="MALE",
                source_of_wealth="SALARY",
            )
        allure.attach(
            json.dumps(resp.json(), ensure_ascii=False, indent=2),
            name="响应体",
            attachment_type=allure.attachment_type.JSON,
        )
        with allure.step("验证响应成功"):
            assert_success(resp)


@allure.feature("KYC")
class TestGetKycResult:

    @allure.story("查询 KYC 审核结果")
    @allure.title("TC-KYC-101 正常查询 KYC 审核结果")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_get_kyc_result(self, kyc_api, pdca_account_id):
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

    @allure.story("查询 KYC 审核结果")
    @allure.title("TC-KYC-102 缺少 X-ON-BEHALF-OF header，返回未授权")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_get_kyc_result_missing_header(self, kyc_api):
        """TC-KYC-102 缺少 X-ON-BEHALF-OF header，返回未授权
        前置条件：无
        请求：不传 X-ON-BEHALF-OF header
        预期结果：HTTP 400/401/403
        """
        with allure.step("发送缺少账户 header 的查询请求"):
            resp = kyc_api.get("/v1/kyc/basic/result")
        with allure.step("验证返回未授权"):
            assert resp.status_code in [400, 401, 403], f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("查询 KYC 审核结果")
    @allure.title("TC-KYC-103 无效 accountId 查询 KYC 审核结果，返回错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_get_kyc_result_invalid_account(self, kyc_api):
        """TC-KYC-103 无效 accountId 查询 KYC 审核结果，返回错误
        前置条件：无
        请求：X-ON-BEHALF-OF 传入不存在的 accountId
        预期结果：HTTP 400/401/403/404 或 code≠0000
        """
        with allure.step("发送无效 accountId 查询请求"):
            resp = kyc_api.get_kyc_result(account_id="invalid_account_id_000")
        with allure.step("验证返回错误"):
            assert resp.status_code in [400, 401, 403, 404] or resp.json().get("code") != "0000", \
                f"实际 {resp.status_code}，响应：{resp.json()}"


@allure.feature("KYC")
class TestSaveEnterpriseKyc:
    """保存企业 KYC 基本信息：PUT /v1/kyc/basic/save"""

    @allure.story("保存企业 KYC 基本信息")
    @allure.title("TC-KYC-ENT-001 正常保存企业 KYC 基本信息")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_save_enterprise_kyc_success(self, kyc_api, pdca_account_id):
        """TC-KYC-ENT-001 正常保存企业 KYC 基本信息
        前置条件：已创建 PDCA 企业账户
        请求体：完整 edd + ubos + directors + businessModel + incorporateInfo
        预期结果：HTTP 200，code=0000
        """
        with allure.step("保存企业 KYC 基本信息"):
            resp = kyc_api.save_enterprise_kyc(
                account_id=pdca_account_id,
                edd=_EDD,
                ubos=_UBOS,
                directors=_DIRECTORS,
                business_model=_BUSINESS_MODEL,
                incorporate_info=_INCORPORATE_INFO,
                registration_source="PARTNER_REFERRAL",
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

    @allure.story("保存企业 KYC 基本信息")
    @allure.title("TC-KYC-ENT-002 缺少 incorporateInfo，返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_save_enterprise_kyc_missing_incorporate_info(self, kyc_api, pdca_account_id):
        """TC-KYC-ENT-002 缺少 incorporateInfo，返回参数错误
        前置条件：已创建 PDCA 企业账户
        请求体：缺少 incorporateInfo，其余字段完整
        预期结果：HTTP 400/422 或 code≠0000
        """
        with allure.step("发送缺少 incorporateInfo 的请求"):
            resp = kyc_api.save_enterprise_kyc(
                account_id=pdca_account_id,
                edd=_EDD,
                ubos=_UBOS,
                directors=_DIRECTORS,
                business_model=_BUSINESS_MODEL,
                registration_source="PARTNER_REFERRAL",
            )
        with allure.step("验证返回参数错误"):
            assert resp.status_code in [400, 422] or resp.json().get("code") != "0000", \
                f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("保存企业 KYC 基本信息")
    @allure.title("TC-KYC-ENT-003 缺少 businessModel，返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_save_enterprise_kyc_missing_business_model(self, kyc_api, pdca_account_id):
        """TC-KYC-ENT-003 缺少 businessModel，返回参数错误
        前置条件：已创建 PDCA 企业账户
        请求体：缺少 businessModel，其余字段完整
        预期结果：HTTP 400/422 或 code≠0000
        """
        with allure.step("发送缺少 businessModel 的请求"):
            resp = kyc_api.save_enterprise_kyc(
                account_id=pdca_account_id,
                edd=_EDD,
                ubos=_UBOS,
                directors=_DIRECTORS,
                incorporate_info=_INCORPORATE_INFO,
                registration_source="PARTNER_REFERRAL",
            )
        with allure.step("验证返回参数错误"):
            assert resp.status_code in [400, 422] or resp.json().get("code") != "0000", \
                f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("保存企业 KYC 基本信息")
    @allure.title("TC-KYC-ENT-004 缺少 ubos，返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_save_enterprise_kyc_missing_ubos(self, kyc_api, pdca_account_id):
        """TC-KYC-ENT-004 缺少 ubos，返回参数错误
        前置条件：已创建 PDCA 企业账户
        请求体：缺少 ubos，其余字段完整
        预期结果：HTTP 400/422 或 code≠0000
        """
        with allure.step("发送缺少 ubos 的请求"):
            resp = kyc_api.save_enterprise_kyc(
                account_id=pdca_account_id,
                edd=_EDD,
                directors=_DIRECTORS,
                business_model=_BUSINESS_MODEL,
                incorporate_info=_INCORPORATE_INFO,
                registration_source="PARTNER_REFERRAL",
            )
        with allure.step("验证返回参数错误"):
            assert resp.status_code in [400, 422] or resp.json().get("code") != "0000", \
                f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("保存企业 KYC 基本信息")
    @allure.title("TC-KYC-ENT-005 缺少 directors，返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_save_enterprise_kyc_missing_directors(self, kyc_api, pdca_account_id):
        """TC-KYC-ENT-005 缺少 directors，返回参数错误
        前置条件：已创建 PDCA 企业账户
        请求体：缺少 directors，其余字段完整
        预期结果：HTTP 400/422 或 code≠0000
        """
        with allure.step("发送缺少 directors 的请求"):
            resp = kyc_api.save_enterprise_kyc(
                account_id=pdca_account_id,
                edd=_EDD,
                ubos=_UBOS,
                business_model=_BUSINESS_MODEL,
                incorporate_info=_INCORPORATE_INFO,
                registration_source="PARTNER_REFERRAL",
            )
        with allure.step("验证返回参数错误"):
            assert resp.status_code in [400, 422] or resp.json().get("code") != "0000", \
                f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("保存企业 KYC 基本信息")
    @allure.title("TC-KYC-ENT-006 空请求体，返回参数错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_save_enterprise_kyc_empty_body(self, kyc_api, pdca_account_id):
        """TC-KYC-ENT-006 空请求体，返回参数错误
        前置条件：已创建 PDCA 企业账户
        请求体：{}
        预期结果：HTTP 400/422 或 code≠0000
        """
        with allure.step("发送空请求体"):
            resp = kyc_api.save_enterprise_kyc(account_id=pdca_account_id)
        with allure.step("验证返回参数错误"):
            assert resp.status_code in [400, 422] or resp.json().get("code") != "0000", \
                f"实际 {resp.status_code}，响应：{resp.json()}"

    @allure.story("保存企业 KYC 基本信息")
    @allure.title("TC-KYC-ENT-007 无效 accountId，返回未授权或账户不存在")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_save_enterprise_kyc_invalid_account(self, kyc_api):
        """TC-KYC-ENT-007 无效 accountId，返回未授权或账户不存在
        前置条件：无
        请求体：完整字段，X-ON-BEHALF-OF 传入不存在的 accountId
        预期结果：HTTP 400/401/403/404
        """
        with allure.step("发送无效 accountId 请求"):
            resp = kyc_api.save_enterprise_kyc(
                account_id="invalid_account_id_000",
                edd=_EDD,
                ubos=_UBOS,
                directors=_DIRECTORS,
                business_model=_BUSINESS_MODEL,
                incorporate_info=_INCORPORATE_INFO,
                registration_source="PARTNER_REFERRAL",
            )
        with allure.step("验证返回错误"):
            assert resp.status_code in [400, 401, 403, 404] or resp.json().get("code") != "0000", \
                f"实际 {resp.status_code}，响应：{resp.json()}"
