from api.base_client import BaseClient


class BeneficiaryAPI(BaseClient):
    """收款人接口"""

    def create_beneficiary(self, account_id: str, currencies: list, bank_location: str,
                           account_nick_name: str, beneficiary_type: str, account_type: str,
                           beneficiary_name: str, bank_swift_code: str = None,
                           bank_name: str = None, bank_account_number: str = None,
                           iban: str = None, country_dial_code: str = None,
                           contact_phone: str = None, recipient_location: str = None,
                           recipient_province: str = None, street1: str = None):
        """创建法币收款人"""
        payload = {
            "currencies": currencies,
            "bankLocation": bank_location,
            "accountNickName": account_nick_name,
            "beneficiaryType": beneficiary_type,
            "accountType": account_type,
            "beneficiaryName": beneficiary_name,
        }
        if bank_swift_code is not None:
            payload["bankSwiftCode"] = bank_swift_code
        if bank_name is not None:
            payload["bankName"] = bank_name
        if bank_account_number is not None:
            payload["bankAccountNumber"] = bank_account_number
        if iban is not None:
            payload["iban"] = iban
        if country_dial_code is not None:
            payload["countryDialCode"] = country_dial_code
        if contact_phone is not None:
            payload["contactPhone"] = contact_phone
        if recipient_location is not None:
            payload["recipientLocation"] = recipient_location
        if recipient_province is not None:
            payload["recipientProvince"] = recipient_province
        if street1 is not None:
            payload["street1"] = street1
        return self.post("/v1/beneficiary/create",
                         headers={"X-ON-BEHALF-OF": account_id},
                         json=payload)

    def create_beneficiary_v2(self, account_id: str, currencies: list, bank_location: str,
                              account_nick_name: str, beneficiary_type: str, account_type: str,
                              beneficiary_name: str, bank_swift_code: str = None,
                              bank_name: str = None, bank_account_number: str = None,
                              iban: str = None, country_dial_code: str = None,
                              contact_phone: str = None, recipient_location: str = None,
                              recipient_province: str = None, street1: str = None):
        """创建法币收款人 V2"""
        payload = {
            "currencies": currencies,
            "bankLocation": bank_location,
            "accountNickName": account_nick_name,
            "beneficiaryType": beneficiary_type,
            "accountType": account_type,
            "beneficiaryName": beneficiary_name,
        }
        if bank_swift_code is not None:
            payload["bankSwiftCode"] = bank_swift_code
        if bank_name is not None:
            payload["bankName"] = bank_name
        if bank_account_number is not None:
            payload["bankAccountNumber"] = bank_account_number
        if iban is not None:
            payload["iban"] = iban
        if country_dial_code is not None:
            payload["countryDialCode"] = country_dial_code
        if contact_phone is not None:
            payload["contactPhone"] = contact_phone
        if recipient_location is not None:
            payload["recipientLocation"] = recipient_location
        if recipient_province is not None:
            payload["recipientProvince"] = recipient_province
        if street1 is not None:
            payload["street1"] = street1
        return self.post("/v2/beneficiary/create",
                         headers={"X-ON-BEHALF-OF": account_id},
                         json=payload)
