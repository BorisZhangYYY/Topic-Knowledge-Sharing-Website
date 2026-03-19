from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt


def create_access_token(
    subject: str,
    secret_key: str,
    expires_in_seconds: int = 7 * 24 * 60 * 60,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """创建 JWT 访问令牌。

    Args:
        subject: 主题标识符，通常是用户 ID 或用户名。
        secret_key: JWT 签名密钥。
        expires_in_seconds: 令牌有效期（秒）。
        extra_claims: 可选的额外声明，嵌入到令牌中。

    Returns:
        编码后的 JWT 字符串。
    """
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return str(token)


def decode_token(token: str, secret_key: str) -> Dict[str, Any]:
    """解码并验证 JWT 令牌。

    Args:
        token: 编码后的 JWT 令牌。
        secret_key: JWT 签名密钥。

    Returns:
        解码后的令牌负载。
    """
    payload: Dict[str, Any] = jwt.decode(token, secret_key, algorithms=["HS256"])
    return payload
