import requests
import jsonschema


def assert_schema(body: dict, schema: dict):
    """校验响应体是否符合 JSON Schema，不符合时输出详细错误"""
    try:
        jsonschema.validate(instance=body, schema=schema)
    except jsonschema.ValidationError as e:
        raise AssertionError(
            f"Schema 校验失败：{e.message}\n"
            f"字段路径：{' -> '.join(str(p) for p in e.absolute_path)}\n"
            f"实际值：{e.instance}"
        )


def assert_success(response: requests.Response) -> dict:
    """验证 HTTP 200 且业务 code=0，返回响应体"""
    assert response.status_code == 200, (
        f"期望状态码 200，实际 {response.status_code}，响应：{response.text}"
    )
    body = response.json()
    assert body.get("code") == "0000", (
        f"期望 code=0000，实际 code={body.get('code')}，msg={body.get('msg')}"
    )
    return body


def assert_error(response: requests.Response,
                 expected_http_code: int = None,
                 expected_biz_code: int = None) -> dict:
    """验证错误响应"""
    if expected_http_code:
        assert response.status_code == expected_http_code, (
            f"期望状态码 {expected_http_code}，实际 {response.status_code}"
        )
    body = response.json()
    if expected_biz_code:
        assert body.get("code") == expected_biz_code, (
            f"期望业务码 {expected_biz_code}，实际 {body.get('code')}"
        )
    return body


def assert_field(body: dict, *field_path: str):
    """验证嵌套字段存在且不为 None，返回字段值"""
    data = body
    path_str = " -> ".join(field_path)
    for field in field_path:
        assert field in data, f"字段 [{path_str}] 不存在，响应：{body}"
        data = data[field]
    assert data is not None, f"字段 [{path_str}] 值为 None"
    return data


def assert_response_time(response: requests.Response, max_ms: int = 2000):
    """验证接口响应时间不超过阈值"""
    elapsed_ms = response.elapsed.total_seconds() * 1000
    assert elapsed_ms <= max_ms, f"响应超时：{elapsed_ms:.0f}ms > {max_ms}ms"


def assert_account_status(body: dict, expected_status: str):
    """验证账户状态字段"""
    actual = body.get("data", {}).get("status")
    assert actual == expected_status, (
        f"期望账户状态 [{expected_status}]，实际 [{actual}]"
    )


def assert_link_status(body: dict, expected_status: str):
    """验证 Link 状态字段"""
    actual = body.get("data", {}).get("status")
    assert actual == expected_status, (
        f"期望 Link 状态 [{expected_status}]，实际 [{actual}]"
    )
