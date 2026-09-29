import uuid

import pytest

from api.account_api import AccountAPI
from api.address_api import AddressAPI
from api.fee_api import FeeAPI
from api.genius_api import GeniusAPI
from api.kyc_api import KycAPI
from api.withdraw_api import WithdrawAPI
from api.kyt_api import KytAPI
from api.mock_api import MockAPI
from api.payment_api import PaymentAPI
from api.refund_api import RefundAPI
from service.payment_service import PaymentService
from service.refund_service import RefundService
from utils.assertions import assert_success
from utils.data_loader import load_yaml
from utils.db_client import query_one


# ─── API 客户端 ───────────────────────────────────────

@pytest.fixture(scope="session")
def fee_api():
    client = FeeAPI(role="merchant")
    yield client
    client.close()


@pytest.fixture(scope="session")
def account_api():
    client = AccountAPI(role="merchant")
    yield client
    client.close()


@pytest.fixture(scope="session")
def genius_api():
    client = GeniusAPI(role="merchant")
    yield client
    client.close()


@pytest.fixture(scope="session")
def payment_api():
    client = PaymentAPI(role="merchant")
    yield client
    client.close()


@pytest.fixture(scope="session")
def kyt_api():
    client = KytAPI(role="risk")
    yield client
    client.close()


@pytest.fixture(scope="session")
def kyc_api():
    client = KycAPI(role="merchant")
    yield client
    client.close()


@pytest.fixture(scope="session")
def address_api():
    client = AddressAPI(role="merchant")
    yield client
    client.close()


@pytest.fixture(scope="session")
def refund_api():
    client = RefundAPI(role="finance")
    yield client
    client.close()


@pytest.fixture(scope="session")
def mock_api():
    client = MockAPI(role="merchant")
    yield client
    client.close()


@pytest.fixture(scope="session")
def withdraw_api():
    client = WithdrawAPI(role="merchant")
    yield client
    client.close()


# ─── 业务服务层 ──────────────────────────────────────

@pytest.fixture(scope="session")
def payment_service(payment_api, mock_api):
    return PaymentService(payment_api, mock_api)


@pytest.fixture(scope="session")
def refund_service(kyt_api, refund_api, mock_api):
    return RefundService(kyt_api, refund_api, mock_api)


# ─── 测试数据 ────────────────────────────────────────

@pytest.fixture(scope="session")
def accounts():
    return load_yaml("accounts.yaml")


@pytest.fixture(scope="session")
def payment_cases():
    return load_yaml("payment_cases.yaml")


@pytest.fixture(scope="session")
def pdca_account_id(account_api, accounts):
    """创建 PDCA 账户，返回 accountId，供 KYC 等后续测试使用"""
    external_account_id = f"pdca_{uuid.uuid4().hex[:12]}"
    resp = account_api.create_pdca_account(
        external_account_id,
        accounts["pdca_create"]["registeredEmail"],
    )
    body = assert_success(resp)
    return body["data"]["accountId"]


@pytest.fixture(scope="session")
def pdca_individual_account_id(account_api, accounts):
    """创建 PDCA 个人账户，返回 accountId，供个人 KYC 测试使用"""
    external_account_id = f"pdca_ind_{uuid.uuid4().hex[:12]}"
    resp = account_api.create_pdca_individual_account(
        external_account_id,
        accounts["pdca_create"]["registeredEmail"],
    )
    body = assert_success(resp)
    return body["data"]["accountId"]


@pytest.fixture(scope="session")
def bene_id():
    """从数据库 t_address_ownership_case 表查询 beneId"""
    row = query_one("SELECT bene_id FROM t_address_ownership_case LIMIT 1")
    assert row, "数据库中未找到 t_address_ownership_case 记录"
    return row["bene_id"]


@pytest.fixture(scope="session")
def merchant_order_id():
    """从 addr_mgt 库 t_payment_order_address 表查询 order_id"""
    row = query_one("SELECT order_id FROM t_payment_order_address LIMIT 1", database="addr_mgt")
    assert row, "数据库中未找到 t_payment_order_address 记录"
    return row["order_id"]


@pytest.fixture(scope="session")
def existing_refund_order_id():
    """从数据库查询已存在的退款单 ID"""
    try:
        row = query_one("SELECT refund_order_id FROM t_refund_order LIMIT 1")
    except Exception as e:
        pytest.skip(f"t_refund_order 表不存在或查询失败，跳过退款查询测试：{e}")
    assert row, "数据库中未找到 t_refund_order 记录"
    return row["refund_order_id"]


