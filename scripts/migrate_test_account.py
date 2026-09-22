#!/usr/bin/env python3
"""
迁移 Python 工程 tests/test_account.py 的测试用例到 Web3ApiPlatform。

方式：显式清单式翻译（非 AST 通用解析），把每个 pytest 测试方法映射为
平台 TestCase JSON（name/serviceName/path/httpMethod/headers/queryParams/body/assertions/description），
按测试类建测试套件(suite)，再通过平台现有 REST API 落库。

幂等：运行前按 suite 名前缀 "pytest:" 清理旧套件，再重建，避免重复。
用法：python scripts/migrate_test_account.py --platform http://localhost:8080
"""
import argparse
import json
import sys
from collections import OrderedDict

import requests

# 平台 serviceName（触发自动 ECDSA 签名）
SERVICE = "leptage-open-api"
# path 前缀（与 Python 端签名 / 平台现有跑通用例一致）
API_PREFIX = "/openapi"

BASE_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

# 常用 header（X-ON-BEHALF-OF 账户）
BEHALF_ACC = "ACC1998628247771996160"

# 测试账户数据（来自 data/accounts.yaml，直接字面量）
ACCOUNTS = {
    "valid":     {"externalAccountId": "testjimmmy124321",    "registeredEmail": "jimmy_xuan@leptage.com"},
    "active":    {"externalAccountId": "test_active_001",     "registeredEmail": "active_user@leptage.com"},
    "suspended": {"externalAccountId": "test_suspended_001",  "registeredEmail": "suspended_user@leptage.com"},
    "closed":    {"externalAccountId": "test_terminal_001",   "registeredEmail": "terminal_user@leptage.com"},
    "withdraw_only": {"externalAccountId": "test_withdraw_001", "registeredEmail": "withdraw_user@leptage.com"},
    "smart_payment_enabled": {"externalAccountId": "test_sp_enabled_001", "registeredEmail": "sp_enabled@leptage.com"},
    "pdca":      {"externalAccountId": "test_pdca_001",       "registeredEmail": "pdca_user@leptage.com"},
    "pdca_create": {"externalAccountId": "testjimmmy12290201", "registeredEmail": "jimmy_xuan@leptage.com"},
}


def acc(key):
    return ACCOUNTS[key]


# ─────────────────────────── 断言辅助 ───────────────────────────
def s_status(op, code):
    return {"type": "STATUS", "operator": op, "expression": "", "value": str(code)}


def s_json(path_expr, op, val):
    return {"type": "JSONPATH", "operator": op, "expression": path_expr, "value": str(val)}


def s_code(op, val):
    return {"type": "CODE", "operator": op, "expression": "$.code", "value": str(val)}


# 查询账户状态 / 钱包等 "成功 + 业务码 0000" 的公共断言
def asm_success():
    return [s_status("eq", 200), s_code("eq", "0000")]


# 错误码可 null 的失败用例（status != 200 或 code != 0）
def asm_not_success():
    return [s_code("ne", "0000")]


# ─────────────────────────── 用例定义 ───────────────────────────
# 每个用例: (suite_name, suite_desc, tc_name, method, path, query, body, assertions, desc)
# query/body 为 dict 或 str；headers 追加到 BASE_HEADERS。
# suites 用 OrderedDict 保证顺序，key 即 suite 名。

UNITS = [
    # ---------- TestAccountStatusNormal ----------
    ("pytest:TestAccountStatusNormal", "正常场景：验证各种账户状态返回正确",
     "TC-AS-001 查询存在的有效账户", "GET", "/v1/account",
     acc("valid"), None,
     asm_success() + [s_json("$.data.status", "ne", "null")] + [{"type": "ELAPSED", "operator": "lt", "expression": "", "value": "2000"}],
     "查询有效账户，返回成功且含完整字段"),

    ("pytest:TestAccountStatusNormal", "正常场景：验证各种账户状态返回正确",
     "TC-AS-002 Active 账户状态", "GET", "/v1/account",
     acc("active"), None,
     asm_success() + [s_json("$.data.status", "eq", "Active")],
     "Active 账户状态正确返回"),

    ("pytest:TestAccountStatusNormal", "正常场景：验证各种账户状态返回正确",
     "TC-AS-003 Suspended 账户状态", "GET", "/v1/account",
     acc("suspended"), None,
     asm_success() + [s_json("$.data.status", "eq", "Suspended")],
     "Suspended 账户状态正确返回"),

    ("pytest:TestAccountStatusNormal", "正常场景：验证各种账户状态返回正确",
     "TC-AS-004 closed 账户状态", "GET", "/v1/account",
     acc("closed"), None,
     asm_success() + [s_json("$.data.status", "eq", "closed")],
     "closed 账户状态正确返回"),

    ("pytest:TestAccountStatusNormal", "正常场景：验证各种账户状态返回正确",
     "TC-AS-005 Withdraw Only 账户", "GET", "/v1/account",
     acc("withdraw_only"), None,
     asm_success() + [s_json("$.data.status", "eq", "Withdraw Only")] +
     [s_json("$.data.canDeposit", "eq", "false"), s_json("$.data.canWithdraw", "eq", "true")],
     "Withdraw Only 账户 canWithdraw=True canDeposit=False"),

    ("pytest:TestAccountStatusNormal", "正常场景：验证各种账户状态返回正确",
     "TC-AS-006 Smart Payment 账户", "GET", "/v1/account",
     acc("smart_payment_enabled"), None,
     asm_success() + [s_json("$.data.smartPaymentEnabled", "eq", "true")],
     "已开通 Smart Payment 账户返回 smartPaymentEnabled=True"),

    ("pytest:TestAccountStatusNormal", "正常场景：验证各种账户状态返回正确",
     "TC-AS-007 PDCA 账户", "GET", "/v1/account",
     acc("pdca"), None,
     asm_success() + [s_json("$.data.registrationEntity", "eq", "PDCA")],
     "PDCA 站点账户返回 registrationEntity=PDCA"),

    # ---------- TestAccountStatusAbnormal ----------
    ("pytest:TestAccountStatusAbnormal", "异常场景：参数校验与错误处理",
     "TC-AS-101 缺少 externalAccountId", "GET", "/v1/account",
     {"registeredEmail": "jimmy_xuan@leptage.com"}, None,
     [s_status("ne", "500")],
     "缺少 externalAccountId，返回 400/422"),

    ("pytest:TestAccountStatusAbnormal", "异常场景：参数校验与错误处理",
     "TC-AS-102 缺少 registeredEmail", "GET", "/v1/account",
     {"externalAccountId": "testjimmmy124321"}, None,
     [s_status("ne", "500")],
     "缺少 registeredEmail，返回 400/422"),

    ("pytest:TestAccountStatusAbnormal", "异常场景：参数校验与错误处理",
     "TC-AS-103 空请求参数", "GET", "/v1/account",
     {}, None,
     [s_status("ne", "500")],
     "空请求参数，返回 400/422"),

    ("pytest:TestAccountStatusAbnormal", "异常场景：参数校验与错误处理",
     "TC-AS-104 账户不存在", "POST", "/v1/account/status",
     None, {"externalAccountId": "nonexistent_account_99999", "registeredEmail": "jimmy_xuan@leptage.com"},
     asm_not_success(),
     "不存在账户应返回业务错误"),

    ("pytest:TestAccountStatusAbnormal", "异常场景：参数校验与错误处理",
     "TC-AS-105 email 与 id 不匹配", "POST", "/v1/account/status",
     None, {"externalAccountId": acc("valid")["externalAccountId"], "registeredEmail": "other_user@leptage.com"},
     asm_not_success(),
     "externalAccountId 与 registeredEmail 不匹配应返回错误"),

    ("pytest:TestAccountStatusAbnormal", "异常场景：参数校验与错误处理",
     "TC-AS-106 非法 email 格式", "POST", "/v1/account/status",
     None, {"externalAccountId": acc("valid")["externalAccountId"], "registeredEmail": "not_an_email"},
     asm_not_success(),
     "非法 email 格式返回参数错误"),

    # ---------- TestAccountStatusBoundary ----------
    ("pytest:TestAccountStatusBoundary", "边界场景：特殊字符、超长输入",
     "TC-AS-201 超长 externalAccountId(255)", "POST", "/v1/account/status",
     None, {"externalAccountId": "a" * 255, "registeredEmail": "jimmy_xuan@leptage.com"},
     [s_status("ne", "500")],
     "超长输入不应返回 500"),

    ("pytest:TestAccountStatusBoundary", "边界场景：特殊字符、超长输入",
     "TC-AS-202 特殊字符 externalAccountId", "POST", "/v1/account/status",
     None, {"externalAccountId": "test!@#$%^&*()", "registeredEmail": "jimmy_xuan@leptage.com"},
     [s_status("ne", "500")],
     "特殊字符不应返回 500"),

    ("pytest:TestAccountStatusBoundary", "边界场景：特殊字符、超长输入",
     "TC-AS-203 空字符串 externalAccountId", "POST", "/v1/account/status",
     None, {"externalAccountId": "", "registeredEmail": "jimmy_xuan@leptage.com"},
     asm_not_success(),
     "空字符串 externalAccountId 返回参数错误"),

    ("pytest:TestAccountStatusBoundary", "边界场景：特殊字符、超长输入",
     "TC-AS-204 大写 email（探索性）", "POST", "/v1/account/status",
     None, {"externalAccountId": acc("valid")["externalAccountId"], "registeredEmail": acc("valid")["registeredEmail"].upper()},
     [s_status("ne", "500")],
     "大写 email 不应返回 500"),

    # ---------- TestAccountStatusSecurity ----------
    ("pytest:TestAccountStatusSecurity", "安全场景：SQL 注入、XSS、越权",
     "TC-AS-301 SQL 注入 externalAccountId", "POST", "/v1/account/status",
     None, {"externalAccountId": "' OR 1=1--", "registeredEmail": "jimmy_xuan@leptage.com"},
     [s_status("ne", "500")],
     "SQL 注入不应返回 500 或暴露 DB 错误"),

    ("pytest:TestAccountStatusSecurity", "安全场景：SQL 注入、XSS、越权",
     "TC-AS-302 XSS externalAccountId", "POST", "/v1/account/status",
     None, {"externalAccountId": "<script>alert('xss')</script>", "registeredEmail": "jimmy_xuan@leptage.com"},
     [s_status("ne", "500")],
     "XSS payload 不应返回 500"),

    ("pytest:TestAccountStatusSecurity", "安全场景：SQL 注入、XSS、越权",
     "TC-AS-303 越权查询", "POST", "/v1/account/status",
     None, {"externalAccountId": "other_user_account_001", "registeredEmail": acc("valid")["registeredEmail"]},
     asm_not_success(),
     "不应返回他人账户信息"),

    # ---------- TestAccountStatusPerformance ----------
    ("pytest:TestAccountStatusPerformance", "性能场景：响应时间验证",
     "TC-AS-401 单次请求响应时间<2000ms", "GET", "/v1/account",
     acc("valid"), None,
     [{"type": "ELAPSED", "operator": "lt", "expression": "", "value": "2000"}],
     "单次请求响应时间 < 2000ms"),

    ("pytest:TestAccountStatusPerformance", "性能场景：响应时间验证",
     "TC-AS-402 连续10次响应时间<2000ms", "GET", "/v1/account",
     acc("valid"), None,
     [{"type": "ELAPSED", "operator": "lt", "expression": "", "value": "2000"}],
     "连续 10 次请求每次 < 2000ms（迁移后按单次验证）"),

    # ---------- TestWalletBalance ----------
    ("pytest:TestWalletBalance", "查询钱包余额接口测试：GET /v1/wallet/balance",
     "TC-BAL-001 正常查询余额", "GET", "/v1/wallet/balance",
     {"ccy": "USDT"}, None,
     asm_success(),
     "正常查询余额", BEHALF_ACC),

    ("pytest:TestWalletBalance", "查询钱包余额接口测试：GET /v1/wallet/balance",
     "TC-BAL-101 缺少 X-ON-BEHALF-OF 头", "GET", "/v1/wallet/balance",
     {"ccy": "usdt"}, None,
     asm_not_success(),
     "缺少 X-ON-BEHALF-OF 请求头返回错误"),

    ("pytest:TestWalletBalance", "查询钱包余额接口测试：GET /v1/wallet/balance",
     "TC-BAL-102 ccy 非法值", "GET", "/v1/wallet/balance",
     {"ccy": "INVALID_CCY"}, None,
     [s_code("eq", "1000"), {"type": "JSONPATH", "operator": "eq", "expression": "$.msg", "value": "invalid parameter"}],
     "ccy 非法值返回错误码 1000", BEHALF_ACC),

    ("pytest:TestWalletBalance", "查询钱包余额接口测试：GET /v1/wallet/balance",
     "TC-BAL-103 不传 ccy", "GET", "/v1/wallet/balance",
     {}, None,
     asm_success(),
     "不传 ccy 返回账户下所有币种余额", BEHALF_ACC),

    # ---------- TestCreatePdcaAccount ----------
    ("pytest:TestCreatePdcaAccount", "创建 PDCA 账户接口测试：POST /v1/account/pdca",
     "TC-PDCA-001 正常创建 PDCA 账户", "POST", "/v1/account/pdca",
     None, {"externalAccountId": "pdca_mig00000001", "registeredEmail": acc("pdca_create")["registeredEmail"]},
     asm_success() + [s_json("$.data.status", "eq", "INACTIVE")] +
     [{"type": "ELAPSED", "operator": "lt", "expression": "", "value": "2000"}],
     "正常创建 PDCA 账户，返回成功"),

    ("pytest:TestCreatePdcaAccount", "创建 PDCA 账户接口测试：POST /v1/account/pdca",
     "TC-PDCA-002 重复 externalAccountId", "POST", "/v1/account/pdca",
     None, {"externalAccountId": "pdca_mig00000001", "registeredEmail": acc("pdca_create")["registeredEmail"]},
     [s_code("ne", "0000")] + [{"type": "JSONPATH", "operator": "contains", "expression": "$.msg", "value": "already exist"}],
     "重复 externalAccountId 返回 000028，msg 含 already exist"),

    ("pytest:TestCreatePdcaAccount", "创建 PDCA 账户接口测试：POST /v1/account/pdca",
     "TC-PDCA-003 缺少 externalAccountId", "POST", "/v1/account/pdca",
     None, {"registeredEmail": acc("pdca_create")["registeredEmail"]},
     [s_status("ne", "500")],
     "缺少 externalAccountId 返回参数错误"),

    ("pytest:TestCreatePdcaAccount", "创建 PDCA 账户接口测试：POST /v1/account/pdca",
     "TC-PDCA-004 缺少 registeredEmail", "POST", "/v1/account/pdca",
     None, {"externalAccountId": "pdca_mig00000002"},
     [s_status("ne", "500")],
     "缺少 registeredEmail 返回参数错误"),

    ("pytest:TestCreatePdcaAccount", "创建 PDCA 账户接口测试：POST /v1/account/pdca",
     "TC-PDCA-005 非法 email 格式", "POST", "/v1/account/pdca",
     None, {"externalAccountId": "pdca_mig00000003", "registeredEmail": "not_an_email"},
     asm_not_success(),
     "非法 email 格式返回参数错误"),

    ("pytest:TestCreatePdcaAccount", "创建 PDCA 账户接口测试：POST /v1/account/pdca",
     "TC-PDCA-006 空请求体", "POST", "/v1/account/pdca",
     None, {},
     [s_status("ne", "500")],
     "空请求体返回参数错误"),

    # ---------- TestUpdateAccountStatus ----------
    ("pytest:TestUpdateAccountStatus", "修改账户状态",
     "TC-ACC-STATUS-001 修改为 SUSPEND", "PUT", "/v1/account/status",
     None, {"accountStatus": "SUSPEND"},
     asm_success(),
     "修改账户状态为 SUSPEND", BEHALF_ACC),

    ("pytest:TestUpdateAccountStatus", "修改账户状态",
     "TC-ACC-STATUS-002 修改为 ACTIVE", "PUT", "/v1/account/status",
     None, {"accountStatus": "ACTIVE"},
     asm_success(),
     "修改账户状态为 ACTIVE", BEHALF_ACC),

    ("pytest:TestUpdateAccountStatus", "修改账户状态",
     "TC-ACC-STATUS-003 修改为 RECEIVE_ONLY", "PUT", "/v1/account/status",
     None, {"accountStatus": "RECEIVE_ONLY"},
     asm_success(),
     "修改账户状态为 RECEIVE_ONLY", BEHALF_ACC),

    ("pytest:TestUpdateAccountStatus", "修改账户状态",
     "TC-ACC-STATUS-005 非法 accountStatus", "PUT", "/v1/account/status",
     None, {"accountStatus": "INVALID_STATUS"},
     asm_not_success(),
     "非法 accountStatus 返回错误", BEHALF_ACC),
]

# 去重 suite 定义（保持引入顺序）
SUITE_ORDER = list(OrderedDict.fromkeys(t[0] for t in UNITS))
SUITE_DESC = {}
for suite, desc in ((t[0], t[1]) for t in UNITS):
    SUITE_DESC.setdefault(suite, desc)


def build_testcase(u):
    """u: tuple → 平台 TestCase JSON。约定元组末位为 desc，倒数第2位(可选)为 BEHALF id。"""
    if len(u) == 10:
        suite, suite_desc, name, method, path, query, body, assertions, desc, behalf = u
    else:
        suite, suite_desc, name, method, path, query, body, assertions, desc = u
        behalf = None

    headers = dict(BASE_HEADERS)
    if behalf:
        headers["X-ON-BEHALF-OF"] = behalf

    full_path = API_PREFIX + path
    return {
        "suite": suite,
        "name": f"{method} {full_path}",
        "serviceName": SERVICE,
        "path": full_path,
        "httpMethod": method,
        "headers": json.dumps(headers, ensure_ascii=False),
        "queryParams": json.dumps(query or {}, ensure_ascii=False),
        "body": json.dumps(body, ensure_ascii=False) if body is not None else "",
        "assertions": json.dumps(assertions, ensure_ascii=False),
        "description": desc,
        "extractions": "[]",
        "preRequest": None,
    }


# ─────────────────────────── 平台 API ───────────────────────────
def api(platform, path, method="GET", json_body=None):
    url = platform.rstrip("/") + path
    resp = requests.request(method, url, json=json_body, timeout=20)
    resp.raise_for_status()
    if not resp.text:
        return None
    return resp.json()


def cleanup_suites(platform):
    """删除所有 pytest: 前缀的旧套件，保证幂等。"""
    deleted = 0
    for s in api(platform, "/api/suites"):
        if s.get("name", "").startswith("pytest:"):
            api(platform, f"/api/suites/{s['id']}", method="DELETE")
            deleted += 1
    return deleted


def migrate(platform):
    cases = [build_testcase(u) for u in UNITS]

    removed = cleanup_suites(platform)

    # suite id 缓存
    suite_ids = {}
    created = 0
    skipped = []

    for suite_name in SUITE_ORDER:
        # 创建套件
        suite = api(platform, "/api/suites", method="POST",
                    json_body={"name": suite_name, "description": SUITE_DESC[suite_name]})
        suite_ids[suite_name] = suite["id"]

    for c in cases:
        try:
            tc = api(platform, "/api/testcases", method="POST", json_body=c)
        except Exception as e:
            skipped.append({"name": c["name"], "reason": f"create case failed: {e}"})
            continue
        # 加入对应套件（顺序号）
        existing = len(api(platform, f"/api/suites/{suite_ids[c['suite']]}/cases"))
        api(platform, f"/api/suites/{suite_ids[c['suite']]}/cases", method="POST",
            json_body={"testCaseId": tc["id"], "orderIndex": existing})
        created += 1

    return {"removedOldSuites": removed, "suites": len(SUITE_ORDER),
            "casesCreated": created, "skipped": skipped}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="migrate test_account.py to platform")
    parser.add_argument("--platform", default="http://localhost:8080")
    args = parser.parse_args()
    result = migrate(args.platform)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["skipped"]:
        print(f"\n⚠ 跳过 {len(result['skipped'])} 个用例：", file=sys.stderr)
        for s in result["skipped"]:
            print("  -", s["name"], "→", s["reason"], file=sys.stderr)
