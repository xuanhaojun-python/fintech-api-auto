from api.base_client import BaseClient


class AddressAPI(BaseClient):
    """地址分配接口"""

    def allocate_address(self, merchant_order_id: str, protocol: str,
                         address_purpose: str, legal_entity: str,
                         payment_link_info: dict = None,
                         travel_rule_info: dict = None):
        """根据订单分配地址"""
        payload = {
            "merchantOrderId": merchant_order_id,
            "protocol": protocol,
            "addressPurpose": address_purpose,
            "legalEntity": legal_entity,
        }

        if payment_link_info:
            payload["paymentLinkInfo"] = payment_link_info
        if travel_rule_info:
            payload["travelRuleInfo"] = travel_rule_info
        return self.post("/v1/addresses/allocate", json=payload)

    def create_ownership_case(self, bene_id: str, ccy: str, protocol: str,
                               account_id: str = "ACC2003701647536205824"):
        """初始化地址所有权 Case 并返回 SDK 所需信息"""
        return self.post("/v1/address-ownership/cases",
                         headers={"X-ON-BEHALF-OF": account_id},
                         json={
                             "beneId": bene_id,
                             "ccy": ccy,
                             "protocol": protocol,
                         })

    def check_address_ownership_eligibility(self, bene_id: str,
                                             account_id: str = "ACC2003701647536205824"):
        """地址所有权合格性检查"""
        return self.get(f"/v1/address-ownership/eligibility/{bene_id}",
                        headers={"X-ON-BEHALF-OF": account_id})

    def get_case_by_bene_id(self, bene_id: str,
                             account_id: str = "ACC2003701647536205824"):
        """根据 BeneId 查询 Case 信息"""
        return self.get(f"/v1/address-ownership/cases/benes/{bene_id}",
                        headers={"X-ON-BEHALF-OF": account_id})

    def release_address(self, merchant_order_id: str):
        """释放地址"""
        return self.post("/v1/addresses/release", json={
            "merchantOrderId": merchant_order_id,
        })

    def delete_deposit_address(self, address_id: str):
        """删除地址"""
        return self.delete(f"/v1/address/deposit/{address_id}")

    def create_deposit_address(self, ccy: str, protocol: str, address: str, nick_name: str = None):
        """创建地址"""
        payload = {
            "ccy": ccy,
            "protocol": protocol,
            "address": address,
        }
        if nick_name is not None:
            payload["nickName"] = nick_name
        return self.post("/v1/address/deposit", json=payload)

    def get_deposit_address(self, address_id: str):
        """查询单个入金地址"""
        return self.get(f"/v1/address/deposit/{address_id}")

    def list_deposit_addresses(self, ccy: str = None, chain: str = None,
                               address: str = None, page_index: int = 1,
                               page_size: int = 20):
        """分页查询入金地址"""
        payload = {"pageIndex": page_index, "pageSize": page_size}
        if ccy is not None:
            payload["ccy"] = ccy
        if chain is not None:
            payload["chain"] = chain
        if address is not None:
            payload["address"] = address
        return self.put("/v1/address/deposit", json=payload)

    def create_withdraw_address(self, ccy: str, chain: str, address: str, nick_name: str = None):
        """创建出金地址"""
        payload = {
            "ccy": ccy,
            "chain": chain,
            "address": address,
        }
        if nick_name is not None:
            payload["nickName"] = nick_name
        return self.post("/v1/address/withdraw", json=payload)

    def dispatch_deposit_addresses(self, items: list):
        """批量分配客户入金地址
        items: [{"ccy": "USDT", "protocol": "ETHEREUM", "accountId": "ACC..."}]
        """
        return self.post("/v1/account/deposit-address/dispatch", json=items)
