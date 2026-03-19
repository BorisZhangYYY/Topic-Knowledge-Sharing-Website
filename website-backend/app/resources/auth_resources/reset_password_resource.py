from __future__ import annotations

from typing import Any, Dict, Tuple

from flask import request
from flask_restful import Resource

from app.auth.passwords import hash_password, verify_password
from app.auth.validation import validate_email, validate_password
from app.common_func.validation import require_json_fields
from app.db.connection import get_db_connection
from app.db.user_info_model import USERS_TABLE_NAME
from app.resources.auth_resources.email_verify_resource import is_otp_valid, otp_store


class ResetPasswordResource(Resource):
    """密码重置资源。

    POST /api/auth/reset_success
    ----------------------------
    接受 JSON 请求体::

        {
            "email":        "user@example.com",
            "otp_code":     "123456",
            "new_password": "NewPass1"
        }

    行为
    ---------
    1. 验证所有三个字段都存在且非空。
    2. 验证 ``email`` 格式。
    3. 验证内存中 :data:`otp_store` 的 OTP（必须
       正确且未过期）。
    4. 验证 ``new_password`` 强度规则（>=8 字符，>=1 大写，
       >=1 小写，>=1 数字）。
    5. 通过邮箱查找用户；当未找到账户时返回 404。
    6. 验证新密码与当前密码**不同**。
    7. 在显式事务中更新数据库中的 ``password_hash``。
    8. 从 :data:`otp_store` 中清除 OTP 记录。

    Returns
    -------
    200  ``{"message": "ok", "detail": "password_reset_success"}``
    400  验证错误（缺少字段、邮箱格式错误、密码强度不足、密码相同、
         OTP 无效或过期）。
    404  该邮箱未注册账户。
    500  意外的数据库错误。
    """

    def post(self) -> Tuple[Dict[str, Any], int]:
        """OTP 验证后重置用户密码。

        Returns:
            (json_body, http_status_code) 元组。
        """
        payload: Any = request.get_json(silent=True)

        # ------------------------------------------------------------------
        # 1. 请求体结构检查
        # ------------------------------------------------------------------
        ok, errors = require_json_fields(payload, ("email", "otp_code", "new_password"))
        if not ok:
            return {"message": "validation_error", "errors": errors}, 400

        email: str = str(payload["email"]).strip().lower()
        otp_code: str = str(payload["otp_code"]).strip()
        new_password: str = str(payload["new_password"])

        # ------------------------------------------------------------------
        # 3. 邮箱格式验证
        # ------------------------------------------------------------------
        valid_email, email_err = validate_email(email)
        if not valid_email:
            return {
                "message": "validation_error",
                "errors": {"email": email_err},
            }, 400

        # ------------------------------------------------------------------
        # 4. OTP 验证（必须在密码检查之前进行，以避免
        #    通过错误顺序泄露账户是否存在）
        # ------------------------------------------------------------------
        if not is_otp_valid(email, otp_code):
            return {
                "message": "validation_error",
                "errors": {"otp_code": "Invalid or expired verification code"},
            }, 400

        # ------------------------------------------------------------------
        # 5. 新密码强度验证
        # ------------------------------------------------------------------
        valid_password, password_err = validate_password(new_password)
        if not valid_password:
            return {
                "message": "validation_error",
                "errors": {"new_password": password_err},
            }, 400

        # ------------------------------------------------------------------
        # 6. 通过邮箱获取用户记录
        # ------------------------------------------------------------------
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        SELECT id, password_hash
                        FROM   {USERS_TABLE_NAME}
                        WHERE  email = %s
                        """,
                        (email,),
                    )
                    row = cur.fetchone()
        except Exception as exc:
            return {"message": "database_error", "detail": str(exc)}, 500

        if row is None:
            return {
                "message": "not_found",
                "detail": "No account is associated with that email address",
            }, 404

        user_id: int = int(row[0])
        current_password_hash: str = str(row[1])

        # ------------------------------------------------------------------
        # 7. 确保新密码与现有密码不同
        # ------------------------------------------------------------------
        if verify_password(new_password, current_password_hash):
            return {
                "message": "validation_error",
                "errors": {
                    "new_password": "New password must be different from the current password"
                },
            }, 400

        # ------------------------------------------------------------------
        # 8. 在显式事务中持久化新的密码哈希
        # ------------------------------------------------------------------
        new_password_hash: str = hash_password(new_password)

        try:
            with get_db_connection() as conn:
                with conn.transaction():
                    with conn.cursor() as cur:
                        cur.execute(
                            f"""
                            UPDATE {USERS_TABLE_NAME}
                            SET    password_hash = %s
                            WHERE  id = %s
                            """,
                            (new_password_hash, user_id),
                        )
        except Exception as exc:
            return {"message": "database_error", "detail": str(exc)}, 500

        # ------------------------------------------------------------------
        # 9. 使 OTP 失效，防止重复使用
        # ------------------------------------------------------------------
        otp_store.pop(email, None)

        return {"message": "ok", "detail": "password_reset_success"}, 200
