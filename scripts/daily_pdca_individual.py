"""
定时任务：每天自动在 SIT 环境创建 PDCA 个人账户
运行：TEST_ENV=sit python scripts/daily_pdca_individual.py
"""
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import os
os.environ.setdefault("TEST_ENV", "sit")

from api.account_api import AccountAPI
from utils.assertions import assert_success
from utils.logger import get_logger

logger = get_logger(__name__)

_REGISTERED_EMAIL = "jimmy_xuan@leptage.com"


def run():
    account_api = AccountAPI()
    try:
        external_id = f"pdca_ind_{uuid.uuid4().hex[:8]}"

        logger.info("=== [定时任务] 开始：创建 PDCA 个人账户 ===")
        logger.info("externalAccountId: %s", external_id)

        resp = account_api.create_pdca_individual_account(external_id, _REGISTERED_EMAIL)
        body = assert_success(resp)
        account_id = body["data"]["accountId"]
        logger.info("个人账户创建成功 accountId=%s  status=%s", account_id, body["data"]["status"])

    except Exception as e:
        logger.error("定时任务执行失败：%s", e, exc_info=True)
        sys.exit(1)
    finally:
        account_api.close()


if __name__ == "__main__":
    run()
