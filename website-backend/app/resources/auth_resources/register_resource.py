from __future__ import annotations

from typing import Any, Dict, Tuple

import psycopg.errors
from flask import current_app, request
from flask_restful import Resource

from app.auth.jwt import create_access_token
from app.auth.passwords import hash_password
from app.auth.validation import validate_email, validate_password, validate_username
from app.common_func.validation import require_json_fields
from app.db.connection import get_db_connection
from app.db.schema import ensure_core_tables
from app.db.user_info_model import UserInfo


class RegisterResource(Resource):
    """用户注册资源。

    POST /api/auth/register
    -----------------------
    接受包含以下字段的 JSON 请求体：

    必需字段：
        username (str): 3-30 个字符，字母数字加下划线，以字母开头。
        password (str): 最少 8 个字符，至少 1 个大写字母，至少 1 个小写字母，至少 1 个数字。
        email (str): 有效的邮箱地址，用于密码找回。

    成功时返回 201 和 JWT 访问令牌。
    验证错误时返回 400。
    用户名或邮箱已存在时返回 409。
    数据库意外错误时返回 500。
    """

    def post(self) -> Tuple[Dict[str, Any], int]:
        """注册新用户。

        Returns:
            (json_body, http_status_code) 的元组。
        """
        payload: Any = request.get_json(silent=True)

        ok, errors = require_json_fields(payload, ("username", "password", "email"))
        if not ok:
            return {"message": "validation_error", "errors": errors}, 400

        assert isinstance(payload, dict)
        username: str = str(payload["username"]).strip()
        password: str = str(payload["password"])
        email: str = str(payload["email"]).strip()

        valid_username, username_err = validate_username(username)
        if not valid_username:
            return {"message": "validation_error", "errors": {"username": username_err}}, 400

        valid_password, password_err = validate_password(password)
        if not valid_password:
            return {"message": "validation_error", "errors": {"password": password_err}}, 400

        valid_email, email_err = validate_email(email)
        if not valid_email:
            return {"message": "validation_error", "errors": {"email": email_err}}, 400

        ensure_core_tables()
        password_hash: str = hash_password(password)

        try:
            with get_db_connection() as conn:
                with conn.transaction():
                    with conn.cursor() as cur:
                        cur.execute(
                            f"""
                            INSERT INTO {UserInfo.TABLE_NAME}
                                (username, password_hash, email)
                            VALUES
                                (%s, %s, %s)
                            RETURNING id
                            """,
                            (username, password_hash, email),
                        )
                        row = cur.fetchone()
            user_id: int = int(row[0]) if row else 0
        except psycopg.errors.UniqueViolation as exc:
            detail: str = str(exc).lower()
            if "email" in detail:
                return {"message": "email_already_exists"}, 409
            return {"message": "username_already_exists"}, 409
        except Exception as exc:
            return {"message": "database_error", "detail": str(exc)}, 500

        secret_key: str = str(current_app.config.get("SECRET_KEY", ""))
        token: str = create_access_token(
            subject=str(user_id),
            username=username,
            secret_key=secret_key,
        )

        return (
            {
                "message": "ok",
                "user_id": user_id,
                "username": username,
                "access_token": token,
            },
            201,
        )
