import time

import requests

from config.settings import AUTH_URL, USERNAME, PASSWORD, TIMEOUT
from utils.logger import get_logger

logger = get_logger(__name__)

_REFRESH_BUFFER_SECONDS = 300  # Token 剩余 5 分钟时提前刷新


class TokenManager:
    """单例 Token 管理器：登录获取 Token，支持多角色、自动刷新"""

    _instances: dict = {}

    def __init__(self, role: str = "merchant"):
        self.role = role
        self._token: str = ""
        self._expires_at: float = 0.0

    @classmethod
    def get_instance(cls, role: str = "merchant") -> "TokenManager":
        if role not in cls._instances:
            cls._instances[role] = cls(role)
        return cls._instances[role]

    @classmethod
    def reset(cls):
        """清除所有缓存的 Token 实例（测试结束 teardown 调用）"""
        cls._instances.clear()

    def get_token(self) -> str:
        if self._is_expired():
            self._login()
        return self._token

    def _is_expired(self) -> bool:
        return time.time() >= self._expires_at - _REFRESH_BUFFER_SECONDS

    def _login(self):
        logger.info(f"[{self.role}] 登录获取 Token → {AUTH_URL}")
        resp = requests.post(
            AUTH_URL,
            json={"username": USERNAME, "password": PASSWORD, "role": self.role},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        body = resp.json()
        data = body.get("data")
        if not data or not isinstance(data, dict):
            raise ValueError(f"[{self.role}] 登录响应结构异常，缺少 data 字段: {body}")
        access_token = data.get("accessToken")
        if not access_token:
            raise ValueError(f"[{self.role}] 登录响应缺少 accessToken: {data}")
        self._token = access_token
        expires_in = data.get("expiresIn", 3600)
        self._expires_at = time.time() + expires_in
        logger.info(f"[{self.role}] Token 获取成功，有效期 {expires_in}s")
