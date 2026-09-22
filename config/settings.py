import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

_ROOT = Path(__file__).parent.parent
_ENV_FILE = _ROOT / "config" / "environments.yaml"

CURRENT_ENV = os.getenv("TEST_ENV", "sit")

with open(_ENV_FILE, encoding="utf-8") as _f:
    _all_envs = yaml.safe_load(_f)

if CURRENT_ENV not in _all_envs:
    raise ValueError(f"未知环境：{CURRENT_ENV}，可选值：{list(_all_envs.keys())}")

_env = _all_envs[CURRENT_ENV]

BASE_URL: str = _env["base_url"]
TIMEOUT: int = _env["timeout"]
AUTH_URL: str = _env["auth_url"]
SSL_VERIFY: bool = _env.get("ssl_verify", True)

USERNAME: str = os.getenv(f"{CURRENT_ENV.upper()}_USERNAME", "")
PASSWORD: str = os.getenv(f"{CURRENT_ENV.upper()}_PASSWORD", "")

API_KEY: str = os.getenv(f"{CURRENT_ENV.upper()}_ACCESS_KEY", "")
API_SECRET: str = os.getenv(f"{CURRENT_ENV.upper()}_SECRET_KEY", "")
