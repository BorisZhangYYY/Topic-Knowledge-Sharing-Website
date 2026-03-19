from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Tuple

from flask import current_app, request
from flask_restful import Resource

from app.auth.jwt import create_access_token
from app.auth.passwords import verify_password
from app.common_func.validation import require_json_fields
from app.db.connection import get_db_connection
from app.db.user_info_model import USERS_TABLE_NAME

# ---------------------------------------------------------------------------
# 阈值：如果 last_login_at 为 NULL（首次登录）或超过 7 天未登录，
# 则在响应中标记，以便客户端提示进行邮箱验证。
# ---------------------------------------------------------------------------
_EMAIL_VERIFY_THRESHOLD_DAYS: int = 7


class LoginResource(Resource):
    """用户登录资源。

    POST /api/auth/login
    --------------------
    接受 JSON 请求体::

        {"username": "...", "password": "..."}

    行为
    ----
    - 根据用户名查找用户。
    - 验证提供的密码与存储的哈希值是否匹配。
    - 确定是否需要提示邮箱验证：
        * 首次登录（``last_login_at IS NULL``），**或**
        * 上次登录超过 7 天前。
    - 认证成功时无条件更新 ``last_login_at = NOW()``。
    - 签发签名 JWT 访问令牌。

    Returns
    -------
    200  成功::

            {
                "message": "ok",
                "user_id": <int>,
                "username": <str>,
                "access_token": <str>,
                "needs_email_verify": <bool>
            }

    400  缺少必填字段或字段类型非字符串。
    401  用户名或密码错误。
    500  意外的数据库错误。
    """

    def post(self) -> Tuple[Dict[str, Any], int]:
        """认证用户并返回 JWT 访问令牌。

        Returns:
            (json_body, http_status_code) 的元组。
        """
        payload: Any = request.get_json(silent=True)

        # ------------------------------------------------------------------
        # 1. 存在性检查
        # ------------------------------------------------------------------
        ok, errors = require_json_fields(payload, ("username", "password"))
        if not ok:
            return {"message": "validation_error", "errors": errors}, 400

        username: str = str(payload["username"]).strip()
        password: str = str(payload["password"])

        # ------------------------------------------------------------------
        # 2. 获取用户记录
        # ------------------------------------------------------------------
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        SELECT id, password_hash, last_login_at
                        FROM   {USERS_TABLE_NAME}
                        WHERE  username = %s
                        """,
                        (username,),
                    )
                    row = cur.fetchone()
        except Exception as exc:
            return {"message": "database_error", "detail": str(exc)}, 500

        if row is None:
            # 用户不存在 —— 返回与密码错误相同的消息，以避免用户名枚举攻击。
            return {"message": "invalid_credentials"}, 401

        user_id: int = int(row[0])
        password_hash: str = str(row[1])
        last_login_at: datetime | None = row[2]  # TIMESTAMPTZ → datetime | None

        # ------------------------------------------------------------------
        # 3. 验证密码
        # ------------------------------------------------------------------
        if not verify_password(password, password_hash):
            return {"message": "invalid_credentials"}, 401

        # ------------------------------------------------------------------
        # 4. 确定是否需要提示邮箱验证
        # ------------------------------------------------------------------
        needs_email_verify: bool
        if last_login_at is None:
            # 首次登录
            needs_email_verify = True
        else:
            # 确保带时区的比较
            if last_login_at.tzinfo is None:
                last_login_at = last_login_at.replace(tzinfo=timezone.utc)
            cutoff = datetime.now(timezone.utc) - timedelta(days=_EMAIL_VERIFY_THRESHOLD_DAYS)
            needs_email_verify = last_login_at < cutoff

        # ------------------------------------------------------------------
        # 5. 更新 last_login_at
        # ------------------------------------------------------------------
        try:
            with get_db_connection() as conn:
                with conn.transaction():
                    with conn.cursor() as cur:
                        cur.execute(
                            f"""
                            UPDATE {USERS_TABLE_NAME}
                            SET    last_login_at = NOW()
                            WHERE  id = %s
                            """,
                            (user_id,),
                        )
        except Exception as exc:
            return {"message": "database_error", "detail": str(exc)}, 500

        # ------------------------------------------------------------------
        # 6. 签发 JWT
        # ------------------------------------------------------------------
        secret_key: str = str(current_app.config.get("SECRET_KEY", ""))
        token: str = create_access_token(
            subject=str(user_id),
            secret_key=secret_key,
            extra_claims={"username": username},
        )

        return (
            {
                "message": "ok",
                "user_id": user_id,
                "username": username,
                "access_token": token,
                "needs_email_verify": needs_email_verify,
            },
            200,
        )
