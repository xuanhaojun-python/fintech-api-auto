from api.kyt_api import KytAPI
from api.refund_api import RefundAPI
from api.mock_api import MockAPI
from utils.assertions import assert_success
from utils.logger import get_logger

logger = get_logger(__name__)


class RefundService:
    """退款流程编排"""

    def __init__(self, kyt_api: KytAPI, refund_api: RefundAPI, mock_api: MockAPI):
        self.kyt = kyt_api
        self.refund = refund_api
        self.mock = mock_api

    def complete_refund_now(self, txn_id: str, refund_address: str) -> dict:
        """
        立即退款完整流程：
          1. 查询 KYT Case
          2. KYT Reject（RefundNow）
          3. 查询退款 Case
          4. 风控审核 Pass
          5. 财务审核 Pass
        返回：{"kytCaseId": ..., "refundCaseId": ...}
        """
        logger.info(f"[RefundService] 立即退款开始 txn={txn_id}")

        resp = self.kyt.get_case(txn_id)
        body = assert_success(resp)
        kyt_case_id = body["data"]["caseId"]

        resp = self.kyt.reject(
            kyt_case_id,
            reject_type=["Refund"],
            refund_result="RefundNow",
            refund_address=refund_address,
        )
        assert_success(resp)

        resp = self.refund.list_cases(status="Pending")
        body = assert_success(resp)
        refund_case_id = body["data"]["list"][0]["caseId"]

        resp = self.refund.risk_review(refund_case_id, action="Pass")
        assert_success(resp)

        resp = self.refund.finance_review(refund_case_id, action="Pass")
        assert_success(resp)

        logger.info(f"[RefundService] 退款完成 refundCaseId={refund_case_id}")
        return {"kytCaseId": kyt_case_id, "refundCaseId": refund_case_id}

    def complete_refund_later(self, txn_id: str, final_amount: float,
                               refund_address: str) -> dict:
        """
        延迟退款完整流程：
          1. 查询 KYT Case
          2. KYT Reject（RefundLater）
          3. 查询退款 Case
          4. 风控审核 Pass（含最终金额）
          5. 财务审核 Pass
        返回：{"kytCaseId": ..., "refundCaseId": ...}
        """
        logger.info(f"[RefundService] 延迟退款开始 txn={txn_id}, finalAmount={final_amount}")

        resp = self.kyt.get_case(txn_id)
        body = assert_success(resp)
        kyt_case_id = body["data"]["caseId"]

        resp = self.kyt.reject(
            kyt_case_id,
            reject_type=["Refund"],
            refund_result="RefundLater",
            refund_address=refund_address,
        )
        assert_success(resp)

        resp = self.refund.list_cases(status="Pending")
        body = assert_success(resp)
        refund_case_id = body["data"]["list"][0]["caseId"]

        resp = self.refund.risk_review(refund_case_id, action="Pass",
                                       final_amount=final_amount)
        assert_success(resp)

        resp = self.refund.finance_review(refund_case_id, action="Pass")
        assert_success(resp)

        logger.info(f"[RefundService] 延迟退款完成 refundCaseId={refund_case_id}")
        return {"kytCaseId": kyt_case_id, "refundCaseId": refund_case_id}
