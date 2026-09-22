"""文件上传接口 JSON Schema"""

UPLOAD_FILE = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        "code": {"type": "string"},
        "msg":  {"type": "string"},
        "data": {
            "type": "object",
            "required": ["fileId"],
            "properties": {
                "fileId": {"type": "string", "minLength": 1},
            },
        },
    },
}
