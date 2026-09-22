"""KYC 相关接口 JSON Schema"""

KYC_BASIC_SUCCESS = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        "code": {"type": "string"},
        "msg":  {"type": "string"},
        "data": {"type": "boolean"},
    },
}

SAVE_INDIVIDUAL_KYC = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        "code": {"type": "string"},
        "msg":  {"type": "string"},
        "data": {"type": "boolean"},
    },
}

GET_KYC_RESULT = {
    "type": "object",
    "required": ["code", "msg"],
    "properties": {
        "code": {"type": "string"},
        "msg":  {"type": "string"},
        "data": {
            "type": ["object", "null"],
            "properties": {
                "status": {"type": "string"},
                "result": {"type": ["string", "null"]},
            },
            "additionalProperties": True,
        },
    },
}
