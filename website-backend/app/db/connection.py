from __future__ import annotations

from typing import Any

from flask import current_app

try:
    import psycopg
except Exception:  # 不纳入代码覆盖率统计
    psycopg = None  # type: ignore[assignment]


def get_db_connection() -> "psycopg.Connection[Any]":  # type: ignore[name-defined]
    """使用应用配置中的 DATABASE_DSN 创建 PostgreSQL 连接。"""
    if psycopg is None:
        raise RuntimeError("psycopg is not installed")
    dsn = str(current_app.config.get("DATABASE_DSN", ""))
    return psycopg.connect(dsn, connect_timeout=3)
