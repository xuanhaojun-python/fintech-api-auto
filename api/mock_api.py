from api.base_client import BaseClient


class MockAPI(BaseClient):
    """Mock 控制接口（仅测试环境可用）"""

    def set_travel_rule_result(self, link_id: str, result: str):
        """设置 Travel Rule 引擎返回结果：'Yes' 或 'No'"""
        return self.post("/v1/mock/travel-rule", json={
            "linkId": link_id,
            "result": result,
        })

    def set_ln_scan_result(self, payer_name: str, is_hit: bool):
        """设置 LN 扫描系统返回结果"""
        return self.post("/v1/mock/ln-scan", json={
            "payerName": payer_name,
            "isHit": is_hit,
        })

    def simulate_chain_transaction(self, link_id: str, amount: float,
                                   currency: str = "USDT",
                                   from_address: str = "0xMOCK_FROM"):
        """模拟链上交易到账，触发 LEP 监测流程"""
        return self.post("/v1/mock/chain-transaction", json={
            "linkId": link_id,
            "amount": amount,
            "currency": currency,
            "fromAddress": from_address,
        })
