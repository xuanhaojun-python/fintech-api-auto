from api.base_client import BaseClient


class FeeAPI(BaseClient):
    """费率配置接口"""

    def get_fee_configs(self, account_ids: list):
        """批量获取费率配置"""
        return self.post("/v1/account/fee-config", json={"accountIds": account_ids})
