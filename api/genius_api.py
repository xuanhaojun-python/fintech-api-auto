from api.base_client import BaseClient


class GeniusAPI(BaseClient):
    """Genius 相关接口"""

    def get_purchase_conf(self, account_id: str = None):
        """查询流量卡是否已购买，account_id 可选"""
        headers = {"X-ON-BEHALF-OF": account_id} if account_id else {}
        return self.get("/v1/genius/purchase-conf", headers=headers)

    def get_history(self, account_id: str = None, page_index: int = None,
                    page_size: int = None):
        """查询 Genius 历史记录"""
        headers = {"X-ON-BEHALF-OF": account_id} if account_id else {}
        payload = {}
        if page_index is not None:
            payload["pageIndex"] = page_index
        if page_size is not None:
            payload["pageSize"] = page_size
        return self.post("/v1/genius/history", headers=headers, json=payload)
