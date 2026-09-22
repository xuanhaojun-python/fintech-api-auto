from api.base_client import BaseClient


class RefundAPI(BaseClient):
    """退款接口"""

    def get_case(self, refund_case_id: str):
        """查询退款 Case"""
        return self.get(f"/v1/refund/case/{refund_case_id}")

    def list_cases(self, status: str = "Pending"):
        """查询退款 Case 列表"""
        return self.get("/v1/refund/cases", params={"status": status})

    def risk_review(self, refund_case_id: str, action: str,
                    final_amount: float = None, remark: str = ""):
        """风控审核退款 Case（Pass / Reject）"""
        payload = {"caseId": refund_case_id, "action": action, "remark": remark}
        if final_amount is not None:
            payload["finalRefundAmount"] = final_amount
        return self.post(f"/v1/refund/case/{refund_case_id}/review", json=payload)

    def finance_review(self, refund_case_id: str, action: str):
        """财务审核退款单（Pass / Reject）"""
        return self.post(
            f"/v1/refund/case/{refund_case_id}/finance-review",
            json={"action": action},
        )
