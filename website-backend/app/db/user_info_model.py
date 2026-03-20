from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar


@dataclass(frozen=True)
class UserInfo:
    """user_info 表数据模型。"""

    TABLE_NAME: ClassVar[str] = "user_info"

    id: int
    username: str
    password_hash: str
    email: str | None
    is_active: bool
    email_verified: bool
    last_login_at: datetime | None
    created_at: datetime
