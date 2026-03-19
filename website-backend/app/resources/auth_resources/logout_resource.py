from __future__ import annotations

from typing import Any, Dict, Set, Tuple

from flask import request
from flask_restful import Resource

from app.auth.middleware import require_auth

# ---------------------------------------------------------------------------
# 内存中的 Token 黑名单
# ---------------------------------------------------------------------------
# 一个简单的原始 JWT 字符串集合，用于存储已通过登出显式失效的 token。
# 服务器重启时该集合会被清空 —— 这对于没有 Redis / 持久化存储的 v0.5 开发版本来说是可以接受的。
#
# require_auth 中间件目前不会自动检查此黑名单；检查被故意保留在登出资源中，
# 以便黑名单相关的逻辑保持集中，一旦有了合适的 token 存储（如 Redis），
# 就可以方便地提取到共享的认证层。
# ---------------------------------------------------------------------------

token_blacklist: Set[str] = set()


def is_token_blacklisted(token: str) -> bool:
    """如果 *token* 已被之前的登出操作列入黑名单，则返回 ``True``。

    Args:
        token: 要检查的原始 JWT 字符串。

    Returns:
        当 token 在 :data:`token_blacklist` 中时返回 ``True``。
    """
    return token in token_blacklist


class LogoutResource(Resource):
    """用户登出资源。

    POST /api/auth/logout
    ---------------------
    需要有效的 ``Authorization: Bearer <token>`` 请求头（由
    :func:`~app.auth.middleware.require_auth` 装饰器强制执行）。

    行为
    ---------
    - 从 ``Authorization`` 请求头中提取原始 JWT。
    - 将其添加到模块级别的 :data:`token_blacklist` 集合中，以便后续
      携带相同 token 的请求可以被拒绝。
    - 立即返回成功响应；token 从此刻起被视为已失效。

    Returns
    -------
    200  ``{"message": "ok", "detail": "logged_out"}``
    401  缺少 / 无效 / 过期的 token（由 ``require_auth`` 处理）。
    """

    @require_auth
    def post(self) -> Tuple[Dict[str, Any], int]:
        """将调用者的 JWT 列入黑名单并确认登出。

        Returns:
            一个 (json_body, http_status_code) 元组。
        """
        # require_auth 此时已经验证了 token，因此我们可以
        # 安全地从请求头中提取原始字符串而无需再次检查。
        auth_header: str = request.headers.get("Authorization", "")
        # 请求头格式由 require_auth 保证："Bearer <token>"
        parts = auth_header.split()
        token: str = parts[1] if len(parts) == 2 else ""

        if token:
            token_blacklist.add(token)

        return {"message": "ok", "detail": "logged_out"}, 200
