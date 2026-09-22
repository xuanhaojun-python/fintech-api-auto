"""
定时任务：每天自动在 SIT 环境创建 PDCA 账户 + 提交 KYC
运行：TEST_ENV=sit python scripts/daily_pdca_kyc.py
"""
import json
import logging
import sys
import uuid
from pathlib import Path

# 把项目根目录加入 path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
os.environ.setdefault("TEST_ENV", "sit")

from api.account_api import AccountAPI
from api.kyc_api import KycAPI
from utils.assertions import assert_success
from utils.logger import get_logger
from tests.test_create_pdca_with_kyc import _build_kyc_payload, _REGISTERED_EMAIL

logger = get_logger(__name__)

# 控制台也显示 DEBUG（签名日志）
for _name in ["auth.signer", "api.base_client"]:
    for _h in logging.getLogger(_name).handlers:
        _h.setLevel(logging.DEBUG)


def run():
    account_api = AccountAPI()
    kyc_api = KycAPI()
    try:
        external_id = f"pdca_{uuid.uuid4().hex[:12]}"
        run_id = uuid.uuid4().hex[:8]

        logger.info("=== [定时任务] 开始：创建 PDCA 账户 ===")
        logger.info("externalAccountId: %s", external_id)

        resp = account_api.create_pdca_account(external_id, _REGISTERED_EMAIL)
        body = assert_success(resp)
        account_id = body["data"]["accountId"]
        logger.info("账户创建成功 accountId=%s  status=%s", account_id, body["data"]["status"])

        logger.info("=== [定时任务] 提交 KYC ===")
        kyc_resp = kyc_api.create_kyc_basic(account_id=account_id, **_build_kyc_payload(run_id))
        assert_success(kyc_resp)
        logger.info("KYC 提交成功")
        logger.info("响应：%s", json.dumps(kyc_resp.json(), ensure_ascii=False, indent=2))

    except Exception as e:
        logger.error("定时任务执行失败：%s", e, exc_info=True)
        sys.exit(1)
    finally:
        account_api.close()
        kyc_api.close()


if __name__ == "__main__":
    run()
