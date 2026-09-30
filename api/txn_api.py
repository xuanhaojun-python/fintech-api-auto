from api.base_client import BaseClient


class TxnAPI(BaseClient):
    """交易查询接口"""

    def get_deposit_txn(self, txn_id: str, account_id: str = None):
        """根据 txnId 查询充值交易详情 GET /v1/txns/deposit/{txnId}"""
        headers = {"X-ON-BEHALF-OF": account_id} if account_id else {}
        return self.get(f"/v1/txns/deposit/{txn_id}", headers=headers)

    def list_deposit_txns(self, page_index: int = 1, page_size: int = 10,
                          account_id: str = None, ccy: str = None,
                          status: str = None):
        """分页查询充值交易列表 POST /v1/txns/deposit"""
        headers = {"X-ON-BEHALF-OF": account_id} if account_id else {}
        payload = {"pageIndex": page_index, "pageSize": page_size}
        if ccy is not None:
            payload["ccy"] = ccy
        if status is not None:
            payload["status"] = status
        return self.post("/v1/txns/deposit", headers=headers, json=payload)

    def list_fx_txns(self, page_index: int = 1, page_size: int = 10,
                     account_id: str = None, ccy_pair: str = None,
                     status: str = None):
        """分页查询换汇交易列表 POST /v1/txns/fx"""
        headers = {"X-ON-BEHALF-OF": account_id} if account_id else {}
        payload = {"pageIndex": page_index, "pageSize": page_size}
        if ccy_pair is not None:
            payload["ccyPair"] = ccy_pair
        if status is not None:
            payload["status"] = status
        return self.post("/v1/txns/fx", headers=headers, json=payload)

    def list_withdraw_txns(self, page_index: int = 1, page_size: int = 10,
                           account_id: str = None, ccy: str = None,
                           status: str = None):
        """分页查询出金交易列表 POST /v1/txns/withdraw"""
        headers = {"X-ON-BEHALF-OF": account_id} if account_id else {}
        payload = {"pageIndex": page_index, "pageSize": page_size}
        if ccy is not None:
            payload["ccy"] = ccy
        if status is not None:
            payload["status"] = status
        return self.post("/v1/txns/withdraw", headers=headers, json=payload)

