from __future__ import annotations

from typing import Any, Dict, Tuple


def require_json_fields(payload: Any, required_fields: Tuple[str, ...]) -> Tuple[bool, Dict[str, str]]:
    """验证 JSON 载荷包含必需的字符串字段。

    Args:
        payload: 已解析的 JSON 载荷。
        required_fields: 必需的字段名。

    Returns:
        (is_valid, errors) 元组。如果 is_valid 为 True，则 errors 为空。
    """
    if not isinstance(payload, dict):
        return False, {"payload": "需要 JSON 对象"}

    errors: Dict[str, str] = {}
    for field in required_fields:
        value: Any = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors[field] = "此字段为必填项"
    return not errors, errors
