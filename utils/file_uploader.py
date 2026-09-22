import base64
import binascii
import json
import time
from urllib.parse import urlparse

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from config.settings import BASE_URL, API_KEY, API_SECRET, SSL_VERIFY
from utils.md5_calculator import calculate_md5

_BASE_PATH = urlparse(BASE_URL).path


def _sign_file_upload(path: str, file_md5: str) -> dict:
    """文件上传专用签名：data_to_sign = METHOD + path + timestamp + fileMd5"""
    timestamp = str(int(time.time() * 1000))
    data_to_sign = f"POST{path}{timestamp}{file_md5}"

    print(f"\n[SIGN DEBUG] data_to_sign = {data_to_sign!r}")
    print(f"[SIGN DEBUG] api_key      = {API_KEY[:30]}...")

    key_bytes = binascii.unhexlify(API_SECRET)
    b64_key = base64.b64encode(key_bytes).decode()
    pem_lines = "\n".join(b64_key[i:i + 64] for i in range(0, len(b64_key), 64))
    pem_key = f"-----BEGIN PRIVATE KEY-----\n{pem_lines}\n-----END PRIVATE KEY-----"

    private_key = serialization.load_pem_private_key(pem_key.encode(), password=None)
    signature = private_key.sign(data_to_sign.encode(), ec.ECDSA(hashes.SHA256()))

    return {
        "X-API-KEY": API_KEY,
        "X-API-SIGNATURE": binascii.hexlify(signature).decode(),
        "X-API-NONCE": timestamp,
    }


def upload_file(file_path: str, account_id: str, timeout: int = 60) -> dict:
    """上传文件，签名末尾拼接 MD5，并附带 X-FILE-HASH 请求头"""
    local_md5 = calculate_md5(file_path)
    print(f"本地文件 MD5: {local_md5}")

    path = "/v1/file"
    sign_path = _BASE_PATH + path
    sign_headers = _sign_file_upload(sign_path, local_md5)
    sign_headers["X-ON-BEHALF-OF"] = account_id
    sign_headers["X-FILE-HASH"] = local_md5
    sign_headers["Accept"] = "application/json"

    with open(file_path, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}{path}",
            files={"file": f},
            headers=sign_headers,
            timeout=timeout,
            verify=SSL_VERIFY,
        )

    print(f"Status: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


if __name__ == "__main__":
    upload_file(
        file_path="/Users/photonpay/Downloads/Codex橙皮书.pdf",
        account_id="ACC2069704375315464192",
    )
