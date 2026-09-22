from api.base_client import BaseClient


class KycAPI(BaseClient):
    """KYC 接口"""

    def create_kyc_basic(self, account_id: str, edd: dict = None, ubos: list = None,
                         agent: dict = None, directors: list = None,
                         business_model: dict = None, incorporate_info: dict = None,
                         registration_source: str = None):
        """创建账户 KYC 基本信息"""
        payload = {}
        if edd is not None:
            payload["edd"] = edd
        if ubos is not None:
            payload["ubos"] = ubos
        if agent is not None:
            payload["agent"] = agent
        if directors is not None:
            payload["directors"] = directors
        if business_model is not None:
            payload["businessModel"] = business_model
        if incorporate_info is not None:
            payload["incorporateInfo"] = incorporate_info
        if registration_source is not None:
            payload["registrationSource"] = registration_source
        return self.post("/v1/kyc/basic",
                         headers={"X-ON-BEHALF-OF": account_id},
                         json=payload)

    def save_individual_kyc(self, account_id: str, full_name: str = None, full_name_en: str = None,
                            first_name: str = None, first_name_en: str = None,
                            middle_name: str = None, middle_name_en: str = None,
                            last_name: str = None, last_name_en: str = None,
                            date_of_birth: str = None, nationality: str = None,
                            country_of_residence: str = None, gender: str = None,
                            source_of_wealth: str = None, purpose_of_account: str = None,
                            liveness_check: bool = None, face_image: list = None,
                            id_docs: list = None, contact: dict = None,
                            residence_address: dict = None):
        """保存个人 KYC 数据"""
        payload = {}
        if full_name is not None:
            payload["fullName"] = full_name
        if full_name_en is not None:
            payload["fullNameEn"] = full_name_en
        if first_name is not None:
            payload["firstName"] = first_name
        if first_name_en is not None:
            payload["firstNameEn"] = first_name_en
        if middle_name is not None:
            payload["middleName"] = middle_name
        if middle_name_en is not None:
            payload["middleNameEn"] = middle_name_en
        if last_name is not None:
            payload["lastName"] = last_name
        if last_name_en is not None:
            payload["lastNameEn"] = last_name_en
        if date_of_birth is not None:
            payload["dateOfBirth"] = date_of_birth
        if nationality is not None:
            payload["nationality"] = nationality
        if country_of_residence is not None:
            payload["countryOfResidence"] = country_of_residence
        if gender is not None:
            payload["gender"] = gender
        if source_of_wealth is not None:
            payload["sourceOfWealth"] = source_of_wealth
        if purpose_of_account is not None:
            payload["purposeOfAccount"] = purpose_of_account
        if liveness_check is not None:
            payload["livenessCheck"] = liveness_check
        if face_image is not None:
            payload["faceImage"] = face_image
        if id_docs is not None:
            payload["idDocs"] = id_docs
        if contact is not None:
            payload["contact"] = contact
        if residence_address is not None:
            payload["residenceAddress"] = residence_address
        return self.put("/v1/kyc/individual/basic/save",
                        headers={"X-ON-BEHALF-OF": account_id},
                        json=payload)

    def get_kyc_result(self, account_id: str):
        """查询 KYC 审核结果"""
        return self.get("/v1/kyc/basic/result", headers={"X-ON-BEHALF-OF": account_id})

    def save_enterprise_kyc(self, account_id: str, edd: dict = None, ubos: list = None,
                            agent: dict = None, directors: list = None,
                            business_model: dict = None, incorporate_info: dict = None,
                            registration_source: str = None):
        """保存企业 KYC 数据"""
        payload = {}
        if edd is not None:
            payload["edd"] = edd
        if ubos is not None:
            payload["ubos"] = ubos
        if agent is not None:
            payload["agent"] = agent
        if directors is not None:
            payload["directors"] = directors
        if business_model is not None:
            payload["businessModel"] = business_model
        if incorporate_info is not None:
            payload["incorporateInfo"] = incorporate_info
        if registration_source is not None:
            payload["registrationSource"] = registration_source
        return self.put("/v1/kyc/basic/save",
                         headers={"X-ON-BEHALF-OF": account_id},
                         json=payload)
