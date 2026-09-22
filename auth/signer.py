import base64
import binascii
import json
import time
from urllib.parse import urlparse, parse_qs, urlencode

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from utils.logger import get_logger

logger = get_logger(__name__)


def _sort_query_params(query_string: str) -> str:
    """按 key 字母序排序查询参数（对应 Postman sortQueryParameters）"""
    pairs = []
    for part in query_string.split("&"):
        if "=" in part:
            k, v = part.split("=", 1)
        else:
            k, v = part, ""
        pairs.append((k, v))
    pairs.sort(key=lambda x: x[0])
    return "&".join(f"{k}={v}" for k, v in pairs)


def _compact_json(body_str: str) -> str:
    """压缩 JSON，去除多余空格换行（对应 Postman JSON.stringify(JSON.parse(...))）"""
    return json.dumps(json.loads(body_str), separators=(",", ":"))


def build_sign_headers(method: str, path: str, query: str, body: str, api_key: str, api_secret: str) -> dict:
    """
    生成 ECDSA 签名所需的三个请求头：
      X-API-KEY       → access key
      X-API-SIGNATURE → SHA256withECDSA 签名（hex）
      X-API-NONCE     → 毫秒时间戳

    签名原文：{METHOD}{path}{timestamp}{body}
    """
    method = method.upper()
    timestamp = str(int(time.time() * 1000))

    # 构造 body 部分（与 Postman 逻辑一致）
    if method in ("GET", "DELETE") and query:
        sign_body = _sort_query_params(query)
    elif method in ("POST", "PUT") and body:
        sign_body = _compact_json(body)
    else:
        sign_body = ""

    data_to_sign = f"{method}{path}{timestamp}{sign_body}"

    logger.debug("[SIGN] data_to_sign = %r", data_to_sign)
    logger.debug("[SIGN] api_key      = %s...", api_key[:30])

    # 将 hex 私钥转换为 PEM 格式
    key_bytes = binascii.unhexlify(api_secret)
    b64_key = base64.b64encode(key_bytes).decode()
    pem_lines = "\n".join(b64_key[i:i + 64] for i in range(0, len(b64_key), 64))
    pem_key = f"-----BEGIN PRIVATE KEY-----\n{pem_lines}\n-----END PRIVATE KEY-----"

    # ECDSA SHA256 签名
    private_key = serialization.load_pem_private_key(pem_key.encode(), password=None)
    signature = private_key.sign(data_to_sign.encode(), ec.ECDSA(hashes.SHA256()))
    signature_hex = binascii.hexlify(signature).decode()
    logger.debug("[SIGN] signature    = %s", signature_hex)

    return {
        "X-API-KEY": api_key,
        "X-API-SIGNATURE": signature_hex,
        "X-API-NONCE": timestamp,
    }
