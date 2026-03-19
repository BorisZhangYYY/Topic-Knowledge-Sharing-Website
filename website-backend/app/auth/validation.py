from __future__ import annotations

import re
from typing import Tuple


def validate_username(username: str) -> Tuple[bool, str]:
    """验证用户名字符串。

    规则：
    - 长度必须在 3 到 30 个字符之间（包含）。
    - 只允许使用字母、数字和下划线。
    - 必须以字母开头（a-z 或 A-Z）。

    Args:
        username: 要验证的用户名字符串。

    Returns:
        一个元组 (is_valid, error_message)。如果 is_valid 为 True，
        则 error_message 为空字符串。
    """
    if not username:
        return False, "Username is required"

    if len(username) < 3:
        return False, "Username must be at least 3 characters long"

    if len(username) > 30:
        return False, "Username must not exceed 30 characters"

    if not re.match(r'^[A-Za-z]', username):
        return False, "Username must start with a letter"

    if not re.match(r'^[A-Za-z0-9_]+$', username):
        return False, "Username may only contain letters, digits, and underscores"

    return True, ""


def validate_password(password: str) -> Tuple[bool, str]:
    """验证密码字符串。

    规则：
    - 最少 8 个字符。
    - 至少一个大写字母（A-Z）。
    - 至少一个小写字母（a-z）。
    - 至少一个数字（0-9）。

    Args:
        password: 要验证的明文密码字符串。

    Returns:
        一个元组 (is_valid, error_message)。如果 is_valid 为 True，
        则 error_message 为空字符串。
    """
    if not password:
        return False, "Password is required"

    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"

    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """验证邮箱地址字符串。

    执行基本格式检查：需要非空的本地部分、
    ``@`` 符号、至少包含一个点的非空域名，
    以及至少两个字符的顶级域名。

    Args:
        email: 要验证的邮箱地址字符串。

    Returns:
        一个元组 (is_valid, error_message)。如果 is_valid 为 True，
        则 error_message 为空字符串。
    """
    if not email:
        return False, "Email is required"

    # 基本邮箱正则表达式：local@domain.tld
    pattern = r'^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email address format"

    return True, ""
