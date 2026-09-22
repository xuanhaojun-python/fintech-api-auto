from api.payment_api import PaymentAPI
from api.mock_api import MockAPI
from utils.assertions import assert_success
from utils.logger import get_logger

logger = get_logger(__name__)


class PaymentService:
    """支付流程编排：组合多个 API 调用完成完整业务场景"""

    def __init__(self, payment_api: PaymentAPI, mock_api: MockAPI):
        self.payment = payment_api
        self.mock = mock_api

    def complete_standard_payment(
        self,
        merchant_id: str,
        payer_name: str,
        payer_email: str,
        amount: float,
        payer_address: str = "0xPAYER_ADDR",
        currency: str = "USDT",
        travel_rule_result: str = "No",
    ) -> dict:
        """
        标准支付完整流程：
          1. 创建 Link
          2. 设置 Travel Rule Mock
          3. 检查 Travel Rule
          4. 获取支付地址
          5. 模拟链上到账
        返回：{"linkId": ..., "paymentAddress": ...}
        """
        logger.info(f"[PaymentService] 标准支付开始 merchant={merchant_id}, amount={amount}")

        resp = self.payment.create_link(merchant_id, payer_name, payer_email, amount, currency)
        body = assert_success(resp)
        link_id = body["data"]["linkId"]
        logger.info(f"[PaymentService] Link 创建成功：{link_id}")

        self.mock.set_travel_rule_result(link_id, travel_rule_result)

        resp = self.payment.check_travel_rule(link_id, payer_address)
        assert_success(resp)

        resp = self.payment.get_payment_address(link_id)
        body = assert_success(resp)
        payment_address = body["data"]["address"]

        self.mock.simulate_chain_transaction(link_id, amount, currency, payer_address)

        logger.info(f"[PaymentService] 标准支付完成 linkId={link_id}")
        return {"linkId": link_id, "paymentAddress": payment_address}

    def complete_travel_rule_payment(
        self,
        merchant_id: str,
        payer_name: str,
        payer_email: str,
        amount: float,
        payer_address: str,
        tr_info: dict,
        currency: str = "USDT",
    ) -> dict:
        """
        需要提交 Travel Rule 信息的支付流程：
          1. 创建 Link
          2. Mock Travel Rule 命中
          3. 检查 Travel Rule
          4. 提交 TR 信息
          5. 获取支付地址
        返回：{"linkId": ..., "paymentAddress": ...}
        """
        logger.info(f"[PaymentService] TR 支付开始 merchant={merchant_id}, amount={amount}")

        resp = self.payment.create_link(merchant_id, payer_name, payer_email, amount, currency)
        body = assert_success(resp)
        link_id = body["data"]["linkId"]

        self.mock.set_travel_rule_result(link_id, "Yes")

        resp = self.payment.check_travel_rule(link_id, payer_address)
        assert_success(resp)

        resp = self.payment.submit_travel_rule_info(link_id, tr_info)
        assert_success(resp)

        resp = self.payment.get_payment_address(link_id)
        body = assert_success(resp)

        logger.info(f"[PaymentService] TR 支付完成 linkId={link_id}")
        return {"linkId": link_id, "paymentAddress": body["data"]["address"]}
