import time

from config.settings import BASE_URL, TIMEOUT, API_KEY, API_SECRET
from auth.signer import build_sign_headers
from urllib.parse import urlparse
import requests

from utils.logger import get_logger

logger = get_logger(__name__)

_BASE_PATH = urlparse(BASE_URL).path


class FileAPI:
    """文件上传接口"""

    def __init__(self, role: str = "merchant"):
        self.role = role
        self.base_url = BASE_URL
        self._session = requests.Session()

    def upload_file(self, file_path: str, account_id: str = "ACC1998628247771996160", file_field: str = "file") -> requests.Response:
        """上传文件，返回文件 ID。
        POST /v1/file
        file_path: 本地文件路径
        account_id: X-ON-BEHALF-OF 请求头值
        file_field: 表单字段名，默认 'file'
        """
        path = "/v1/file"
        sign_path = _BASE_PATH + path
        # multipart 请求签名 body 为空
        sign_headers = build_sign_headers("POST", sign_path, "", "", API_KEY, API_SECRET)
        sign_headers["X-ON-BEHALF-OF"] = account_id
        sign_headers["Accept"] = "application/json"
        # Content-Type 由 requests 自动生成（含 boundary），不手动设置

        with open(file_path, "rb") as f:
            files = {file_field: f}
            start = time.time()
            resp = self._session.post(
                f"{self.base_url}{path}",
                files=files,
                headers=sign_headers,
                timeout=TIMEOUT,
            )
        elapsed_ms = (time.time() - start) * 1000
        log_msg = f"POST {path} → {resp.status_code} ({elapsed_ms:.0f}ms)"
        if resp.ok:
            logger.info(log_msg)
        else:
            logger.warning(f"{log_msg} | body={resp.text[:300]}")
        return resp

    def close(self):
        self._session.close()
