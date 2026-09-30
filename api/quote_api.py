from api.base_client import BaseClient


class QuoteAPI(BaseClient):
    """换汇询价接口"""

    def get_quote(self, ccy_pair: str, account_id: str = None):
        """换汇询价 GET /v1/quote
        ccy_pair: 货币对，如 USDT-USD、USD-USDT
        """
        headers = {"X-ON-BEHALF-OF": account_id} if account_id else {}
        return self.get("/v1/quote", headers=headers, params={"ccyPair": ccy_pair})
