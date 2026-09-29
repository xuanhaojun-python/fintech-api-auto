from api.base_client import BaseClient


class WithdrawAPI(BaseClient):
    """加密货币提款接口"""

    def withdraw_crypto(self, ccy: str, amount: str, bene_id: str, chain: str,
                        request_id: str, verified_data: dict = None,
                        account_id: str = None):
        """POST /v1/withdraw/crypto 发起加密货币提款"""
        headers = {"X-ON-BEHALF-OF": account_id} if account_id else {}
        payload = {
            "ccy": ccy,
            "amount": amount,
            "beneId": bene_id,
            "chain": chain,
            "requestId": request_id,
        }
        if verified_data is not None:
            payload["verifiedData"] = verified_data
        return self.post("/v1/withdraw/crypto", headers=headers, json=payload)
