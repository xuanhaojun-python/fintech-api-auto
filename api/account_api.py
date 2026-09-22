from api.base_client import BaseClient


class AccountAPI(BaseClient):
    """账户管理接口"""

    def create_account(self, external_account_id: str, registered_email: str):
        """创建账户（externalAccountId 不可重复）"""
        return self.post("/v1/account", json={
            "externalAccountId": external_account_id,
            "registeredEmail": registered_email,
        })

    def create_pdca_account(self, external_account_id: str, registered_email: str):
        """创建 PDCA 账户（externalAccountId 不可重复）"""
        return self.post("/v1/account/pdca", json={
            "externalAccountId": external_account_id,
            "registeredEmail": registered_email,
        })

    def create_pdca_enterprise_account(self, external_account_id: str, registered_email: str,
                                       member_registration_source: str = "PHP"):
        """创建 PDCA 企业账户"""
        return self.post("/v1/account/pdca", json={
            "externalAccountId": external_account_id,
            "registeredEmail": registered_email,
            "memberRegistrationSource": member_registration_source,
        })

    def create_pdca_individual_account(self, external_account_id: str, registered_email: str,
                                        registration_source: str = "PDCA",
                                        member_registration_source: str = "SYKKA"):
        """创建 PDCA 个人账户（externalAccountId 不可重复）"""
        return self.post("/v1/account/pdca/individual", json={
            "externalAccountId": external_account_id,
            "registeredEmail": registered_email,
            "registrationSource": registration_source,
            "memberRegistrationSource": member_registration_source,
        })

    def get_status(self, external_account_id: str, registered_email: str):
        """查询账户状态"""
        return self.get("/v1/account", params={
            "externalAccountId": external_account_id,
            "registeredEmail": registered_email,
        })

    def list_accounts(self, page: int = 1, page_size: int = 20):
        """查询账户列表"""
        return self.get("/v1/accounts", params={"page": page, "pageSize": page_size})

    def get_wallet_balance(self, account_id: str = "ACC1998628247771996160", ccy: str = "USDT"):
        """查询钱包余额"""
        return self.get("/v1/wallet/balance", headers={"X-ON-BEHALF-OF": account_id}, params={"ccy": ccy})

    def get_connect_fee_config(self, account_id: str):
        """获取子账号费率配置"""
        return self.get("/v1/account/connect/fee-config",
                        headers={"X-ON-BEHALF-OF": account_id})

    def get_master_fee_config(self, account_id: str):
        """获取主账号费率配置"""
        return self.get("/v1/account/master/fee-config",
                        headers={"X-ON-BEHALF-OF": account_id})

    def update_account_status(self, account_id: str = "ACC2046490376348372992",
                               account_status: str = "SUSPEND"):
        """修改账户状态"""
        return self.put("/v1/account/status",
                        headers={"X-ON-BEHALF-OF": account_id},
                        json={"accountStatus": account_status})

    def charge_off_quote(self, account_id: str, ccy_pair: str, sell_amount: str = "10"):
        """Charge off 询价（左卖右买，如 USDT-USD 或 USD-USDT）"""
        return self.get("/v1/wallet/quote",
                        headers={"X-ON-BEHALF-OF": account_id},
                        params={"ccyPair": ccy_pair, "sellAmount": sell_amount})

    def wallet_exchange(self, account_id: str, quote_id: str, request_id: str,
                        ccy_pair: str, sell_amount: str):
        """钱包兑换（使用报价 ID 执行兑换）"""
        return self.post("/v1/wallet/exchange",
                         headers={"X-ON-BEHALF-OF": account_id},
                         json={
                             "requestId": request_id,
                             "ccyPair": ccy_pair,
                             "sellAmount": sell_amount,
                             "quoteId": quote_id,
                         })
