"""账户相关接口 JSON Schema"""

CREATE_PDCA_ACCOUNT = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        "code": {"type": "string"},
        "msg":  {"type": "string"},
        "data": {
            "type": "object",
            "required": ["accountId", "externalAccountId", "registeredEmail", "status"],
            "properties": {
                "accountId":         {"type": "string", "pattern": r"^ACC\d+$"},
                "externalAccountId": {"type": "string"},
                "registeredEmail":   {"type": "string"},
                "status":            {"type": "string", "enum": ["INACTIVE", "ACTIVE", "SUSPENDED"]},
                "userId":            {"type": "string"},
            },
            "additionalProperties": True,
        },
    },
}

CREATE_PDCA_INDIVIDUAL_ACCOUNT = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        "code": {"type": "string"},
        "msg":  {"type": "string"},
        "data": {
            "type": "object",
            "required": ["accountId", "externalAccountId", "registeredEmail", "status", "userId"],
            "properties": {
                "accountId":         {"type": "string", "pattern": r"^ACC\d+$"},
                "externalAccountId": {"type": "string"},
                "registeredEmail":   {"type": "string"},
                "status":            {"type": "string", "enum": ["INACTIVE", "ACTIVE", "SUSPENDED"]},
                "userId":            {"type": "string", "pattern": r"^USR\d+$"},
            },
            "additionalProperties": True,
        },
    },
}

GET_ACCOUNT_STATUS = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        "code": {"type": "string"},
        "msg":  {"type": "string"},
        "data": {
            "type": "object",
            "required": ["status"],
            "properties": {
                "accountId":   {"type": "string"},
                "status":      {"type": "string"},
                "canDeposit":  {"type": "boolean"},
                "canWithdraw": {"type": "boolean"},
            },
            "additionalProperties": True,
        },
    },
}
