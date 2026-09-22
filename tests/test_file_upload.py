"""
文件上传接口测试
POST /v1/file
运行：TEST_ENV=uat pytest tests/test_file_upload.py -s -v
"""
import io
import struct
import zlib

import allure
import pytest

from api.file_api import FileAPI
from utils.assertions import assert_success


def _make_minimal_png() -> bytes:
    """生成一个 1×1 白色像素的最小合法 PNG（纯 Python，无需第三方库）"""
    def chunk(name: bytes, data: bytes) -> bytes:
        c = name + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    raw = b"\x00\xFF\xFF\xFF"                          # filter byte + RGB
    idat = chunk(b"IDAT", zlib.compress(raw))
    iend = chunk(b"IEND", b"")
    return signature + ihdr + idat + iend


@pytest.fixture
def tmp_png(tmp_path):
    """生成临时 PNG 测试文件，测试结束后自动清理"""
    png_file = tmp_path / "test_doc.png"
    png_file.write_bytes(_make_minimal_png())
    return str(png_file)


@allure.feature("文件上传")
class TestFileUpload:

    @allure.story("正常上传")
    @allure.title("TC-FILE-001 正常上传 PNG 文件，返回文件 ID")
    @pytest.mark.smoke
    def test_upload_file_success(self, tmp_png):
        """TC-FILE-001 上传合法文件，期望返回 200 及文件 ID"""
        file_api = FileAPI(role="merchant")
        try:
            with allure.step("上传文件"):
                resp = file_api.upload_file(tmp_png)
                print(f"\n响应状态码: {resp.status_code}")
                print(f"响应体: {resp.text}")

            with allure.step("验证响应成功"):
                body = assert_success(resp)

            with allure.step("验证返回文件 ID"):
                file_id = body.get("data")
                assert file_id, f"响应中未找到文件 ID，响应体: {body}"
                print(f"文件 ID: {file_id}")
                allure.attach(str(file_id), name="文件 ID", attachment_type=allure.attachment_type.TEXT)
        finally:
            file_api.close()
