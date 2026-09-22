import json
import time
from urllib.parse import urlparse, urlencode

import requests

from config.settings import BASE_URL, TIMEOUT, API_KEY, API_SECRET, SSL_VERIFY

_BASE_PATH = urlparse(BASE_URL).path  # e.g. "/openapi"
from auth.signer import build_sign_headers
from utils.logger import get_logger

logger = get_logger(__name__)

_DEFAULT_RETRIES = 1


class BaseClient:
    """统一 HTTP 客户端：ECDSA 签名、请求/响应日志、失败重试"""

    def __init__(self, role: str = "merchant", retries: int = _DEFAULT_RETRIES):
        self.role = role
        self.retries = retries
        self.base_url = BASE_URL
        self._session = requests.Session()

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", TIMEOUT)

        # 提取 query string 和 body 用于签名
        # 签名使用原始未编码的参数（与 Postman request.url 行为一致）
        params = kwargs.get("params", {})
        # 必须与 requests 实际发送的 URL 一致（会 URL 编码特殊字符，如 @ → %40）
        query = urlencode(params) if params else ""

        body = ""
        if "json" in kwargs:
            # 压缩 JSON，签名和发送保持一致
            body = json.dumps(kwargs.pop("json"), separators=(",", ":"))
            kwargs["data"] = body
        elif "data" in kwargs and isinstance(kwargs["data"], str):
            body = kwargs["data"]

        # 签名 path = base path + api path，如 /openapi/v1/account/status
        sign_path = _BASE_PATH + path
        sign_headers = build_sign_headers(method, sign_path, query, body, API_KEY, API_SECRET)

        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"
        headers.update(sign_headers)
        kwargs["headers"] = headers

        resp = None
        for attempt in range(self.retries + 1):
            start = time.time()
            resp = self._session.request(method, url, verify=SSL_VERIFY, **kwargs)
            elapsed_ms = (time.time() - start) * 1000

            log_msg = f"{method} {path} → {resp.status_code} ({elapsed_ms:.0f}ms)"
            if resp.ok:
                logger.info(log_msg)
            else:
                logger.warning(f"{log_msg} | body={resp.text[:300]}")

            if resp.status_code < 500 or attempt == self.retries:
                return resp

            logger.warning(f"服务端错误，第 {attempt + 1} 次重试...")
            time.sleep(0.5)

        return resp

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.request("DELETE", path, **kwargs)

    def close(self):
        self._session.close()
