from __future__ import annotations

import functools
from typing import Any, Callable, Dict, Tuple, TypeVar

from flask import current_app, g, request
from flask_restful import Resource

from app.auth.jwt import decode_token

F = TypeVar("F", bound=Callable[..., Any])

_UNAUTHORIZED: Tuple[Dict[str, str], int] = ({"message": "unauthorized"}, 401)


def require_auth(fn: F) -> F:
    """强制在资源方法上使用 JWT Bearer 认证的装饰器。

    用法
    -----
    应用于任何 Flask-RESTful 资源方法（``get``、``post`` 等）：

    .. code-block:: python

        class MyResource(Resource):
            @require_auth
            def post(self) -> Tuple[Dict, int]:
                user = g.current_user  # {"user_id": ..., "username": ...}
                ...

    行为
    ----
    - 期望 ``Authorization: Bearer <token>`` 请求头。
    - 使用 :func:`app.auth.jwt.decode_token` 和 ``current_app.config["SECRET_KEY"]``
      解码并验证令牌。
    - 成功时，将解析的身份存储在 ``flask.g.current_user`` 中，格式为::

          {"user_id": str, "username": str}

      然后正常调用被包装的函数。
    - 任何失败（缺少请求头、错误的 scheme、过期的令牌、错误的
      签名、缺少声明）时，返回 ``{"message": "unauthorized"}``
      和 HTTP 401, 不调用被包装的函数。

    Args:
        fn: 要保护的资源方法。

    Returns:
        应用了认证强制执行的包装方法。
    """

    @functools.wraps(fn) # 保留被装饰函数的元信息
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        auth_header: str | None = request.headers.get("Authorization")  # 从请求头中取Authorization字段

        if not auth_header:
            return _UNAUTHORIZED

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return _UNAUTHORIZED

        token: str = parts[1]
        secret_key: str = str(current_app.config.get("SECRET_KEY", ""))

        try:
            payload: Dict[str, Any] = decode_token(token, secret_key)
        except Exception:
            return _UNAUTHORIZED

        user_id: Any = payload.get("sub") 
        username: Any = payload.get("username")

        if user_id is None or username is None:
            return _UNAUTHORIZED

        g.current_user = {
            "user_id": str(user_id),
            "username": str(username),
        }

        return fn(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
