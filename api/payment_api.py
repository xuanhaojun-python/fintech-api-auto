import time

from api.base_client import BaseClient


class PaymentAPI(BaseClient):
    """Smart Payment 接口"""

    def create_link(self, merchant_id: str, payer_name: str,
                    payer_email: str, amount: float, currency: str = "USDT"):
        """创建 Smart Payment Link"""
        return self.post("/v1/smart-payment/link/create", json={
            "merchantId": merchant_id,
            "payerName": payer_name,
            "payerEmail": payer_email,
            "amount": amount,
            "currency": currency,
        })

    def get_link_status(self, link_id: str):
        """查询 Link 状态"""
        return self.get(f"/v1/smart-payment/link/{link_id}/status")

    def check_travel_rule(self, link_id: str, payer_address: str):
        """触发 Travel Rule 检查"""
        return self.post("/v1/smart-payment/travel-rule/check", json={
            "linkId": link_id,
            "payerAddress": payer_address,
        })

    def submit_travel_rule_info(self, link_id: str, tr_info: dict):
        """提交 Travel Rule 信息"""
        return self.post("/v1/smart-payment/travel-rule/submit", json={
            "linkId": link_id,
            **tr_info,
        })

    def get_payment_address(self, link_id: str):
        """获取支付地址"""
        return self.post("/v1/smart-payment/payment-address", json={"linkId": link_id})

    def refund(self, payin_txn_id: str, refund_order_id: str,
               origin_merchant_order_id: str, from_address: str,
               to_address: str, tx_hash: str, amount: str,
               ccy: str = "USDT", protocol: str = "ETHEREUM",
               created_at: int = None, completed_at: int = None,
               status: str = "Succeeded", reason: str = "refund",
               refund_type: str = "PAYMENT"):
        """创建 Crypto Payment 退款"""
        payload = {
            "payinTxnId": payin_txn_id,
            "refundOrderId": refund_order_id,
            "originMerchantOrderId": origin_merchant_order_id,
            "fromAddress": from_address,
            "toAddress": to_address,
            "txHash": tx_hash,
            "amount": amount,
            "ccy": ccy,
            "protocol": protocol,
            "createdAt": created_at if created_at is not None else int(time.time() * 1000),
            "completedAt": completed_at if completed_at is not None else int(time.time() * 1000),
            "status": status,
            "reason": reason,
            "type": refund_type,
        }
        return self.post("/v1/payment/refund", json=payload)

    def get_refund(self, refund_order_id: str):
        """查询退款交易"""
        return self.get("/v1/payment/refund", params={"refundOrderId": refund_order_id})

    def get_txn(self, merchant_order_id: str):
        """查询入金交易"""
        return self.get("/v1/payment/txn", params={"merchantOrderId": merchant_order_id})

    def get_receipt(self, txn_id: str, on_behalf_of: str = None):
        """查看交易凭证"""
        headers = {"X-ON-BEHALF-OF": on_behalf_of} if on_behalf_of else {}
        return self.get(f"/v1/txn/receipt/{txn_id}", headers=headers)

    def download_receipt(self, txn_id: str, on_behalf_of: str = None):
        """下载交易凭证"""
        headers = {"X-ON-BEHALF-OF": on_behalf_of} if on_behalf_of else {}
        return self.post(f"/v1/txn/receipt/download/{txn_id}", headers=headers)
