from __future__ import annotations

import random
import time
from typing import Any, Dict, Tuple

from flask import request
from flask_restful import Resource

from app.auth.validation import validate_email
from app.common_func.validation import require_json_fields

# -----------------------------------------------------------------------------
# 内存中的 OTP 存储
# -----------------------------------------------------------------------------
# 结构: { email: {"code": str, "expires_at": float} }
# expires_at 是 Unix 时间戳 (time.time() + 600 秒)。
# 这是一个简单的开发模式存储 —— 没有 Redis，没有持久化。
# -----------------------------------------------------------------------------

otp_store: Dict[str, Dict[str, Any]] = {}

_OTP_TTL_SECONDS: int = 600  # 10 分钟


def _generate_otp() -> str:
    """生成一个零填充的 6 位 OTP 验证码。

    Returns:
        一个恰好 6 位数字的字符串，例如 ``"042817"``。
    """
    return f"{random.randint(0, 999999):06d}"


def _store_otp(email: str, code: str) -> None:
    """将一个 OTP 条目写入内存存储。

    Args:
        email: 目标邮箱地址（用作字典键）。
        code:  要存储的 6 位 OTP 字符串。
    """
    otp_store[email] = {
        "code": code,
        "expires_at": time.time() + _OTP_TTL_SECONDS,
    }


def is_otp_valid(email: str, code: str) -> bool:
    """检查提供的 OTP 验证码是否正确且未过期。

    Args:
        email: 要查找的邮箱地址。
        code:  调用者提供的 OTP 验证码。

    Returns:
        如果验证码匹配且尚未过期则返回 ``True``，否则返回 ``False``。
    """
    entry = otp_store.get(email)
    if entry is None:
        return False
    if time.time() > entry["expires_at"]:
        # 惰性删除过期条目
        otp_store.pop(email, None)
        return False
    return entry["code"] == code


class EmailVerifyResource(Resource):
    """邮箱验证 / OTP 发送资源。

    POST /api/auth/email_verifying
    --------------------------------
    接受 JSON 请求体::

        {"email": "user@example.com"}

    行为说明
    ---------
    - 验证邮箱格式。
    - 生成一个 6 位 OTP 并将其存储在 :data:`otp_store` 中，TTL 为 10 分钟。
    - 在生产环境中，你应该通过邮件服务提供商发送验证码；在此开发版本中，
      验证码直接返回在响应体中，键名为 ``"code"``，同时包含 ``"detail": "dev_mode"``。

    Returns
    -------
    200  ``{"message": "ok", "code": "<otp>", "detail": "dev_mode"}``
    400  ``{"message": "validation_error", "errors": {"email": "<reason>"}}``
    """

    def post(self) -> Tuple[Dict[str, Any], int]:
        """为给定邮箱生成并（在开发模式下）返回一个 6 位 OTP。

        Returns:
            一个元组 (json_body, http_status_code)。
        """
        payload: Any = request.get_json(silent=True)

        ok, errors = require_json_fields(payload, ("email",))
        if not ok:
            return {"message": "validation_error", "errors": errors}, 400
        email: str = str(payload["email"]).strip().lower()

        valid, email_err = validate_email(email)
        if not valid:
            return {
                "message": "validation_error",
                "errors": {"email": email_err},
            }, 400

        code: str = _generate_otp()
        _store_otp(email, code)

        # ------------------------------------------------------------------
        # 开发模式：由于没有邮件服务器，直接返回 OTP。
        # 在生产环境中，将此代码块替换为实际发送，并返回：
        #   {"message": "ok", "detail": "verification code sent"}
        # ------------------------------------------------------------------
        return {
            "message": "ok",
            "code": code,
            "detail": "dev_mode",
        }, 200
