from __future__ import annotations

from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(password: str) -> str:
    """对明文密码进行哈希处理。

    Args:
        password: 明文密码。

    Returns:
        加盐后的密码哈希。
    """
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """验证明文密码是否与存储的哈希匹配。

    Args:
        password: 明文密码。
        password_hash: 存储的密码哈希。

    Returns:
        如果密码匹配则返回 True。
    """
    return check_password_hash(password_hash, password)
