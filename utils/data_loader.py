import json
from pathlib import Path
from typing import Any

import openpyxl
import yaml

_DATA_DIR = Path(__file__).parent.parent / "data"


def load_yaml(relative_path: str) -> Any:
    """加载 YAML 数据文件，路径相对于 data/ 目录"""
    with open(_DATA_DIR / relative_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(relative_path: str) -> Any:
    """加载 JSON 数据文件，路径相对于 data/ 目录"""
    with open(_DATA_DIR / relative_path, encoding="utf-8") as f:
        return json.load(f)


def load_excel(relative_path: str, sheet_name: str = None) -> list[dict]:
    """
    加载 Excel 数据文件，返回 list of dict（首行为表头）
    路径相对于 data/ 目录
    """
    wb = openpyxl.load_workbook(
        _DATA_DIR / relative_path, read_only=True, data_only=True
    )
    ws = wb[sheet_name] if sheet_name else wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if not rows:
        return []

    headers = [str(h) for h in rows[0]]
    return [
        dict(zip(headers, row))
        for row in rows[1:]
        if any(v is not None for v in row)
    ]
