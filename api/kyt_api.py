from api.base_client import BaseClient


class KytAPI(BaseClient):
    """KYT 审核接口"""

    def get_case(self, txn_id: str):
        """查询 KYT Case"""
        return self.get(f"/v1/kyt/case/{txn_id}")

    def get_ln_cases(self, kyt_case_id: str):
        """查询 LN 扫描 Case 列表"""
        return self.get(f"/v1/kyt/case/{kyt_case_id}/ln-cases")

    def complete_ln_case(self, ln_case_id: str, result: str, remark: str = ""):
        """完成 LN Case 人工排查"""
        return self.post(f"/v1/kyt/ln-case/{ln_case_id}/review", json={
            "result": result,
            "remark": remark,
        })

    def collect_travel_rule_info(self, merchant_order_id: str, txn_type: str,
                                 legal_entity: str, amount: str, ccy: str,
                                 protocol: str):
        """Travel Rule 信息采集"""
        return self.post("/v1/kyt/travel-rule/check", json={
            "merchantOrderId": merchant_order_id,
            "txnType": txn_type,
            "legalEntity": legal_entity,
            "amount": amount,
            "ccy": ccy,
            "protocol": protocol,
        })

    def approve(self, kyt_case_id: str):
        """KYT 一审 Approve"""
        return self.post(f"/v1/kyt/case/{kyt_case_id}/approve")

    def reject(self, kyt_case_id: str, reject_type: list,
               refund_result: str, mark_polluted: bool = False,
               refund_address: str = None, remark: str = ""):
        """KYT 一审 Reject"""
        payload = {
            "caseId": kyt_case_id,
            "rejectType": reject_type,
            "refundResult": refund_result,
            "markAsPolluted": mark_polluted,
            "remark": remark,
        }
        if refund_address:
            payload["refundAddress"] = refund_address
        return self.post(f"/v1/kyt/case/{kyt_case_id}/reject", json=payload)
