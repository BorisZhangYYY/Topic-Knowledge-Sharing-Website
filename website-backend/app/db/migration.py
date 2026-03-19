from __future__ import annotations

from typing import Iterable, List

from app.db.connection import get_db_connection
from app.db.user_schema_migration import (
    CREATE_SCHEMA_MIGRATIONS_TABLE_SQL,
    CREATE_USERS_TABLE_SQL,
    MIGRATIONS,
)


# ---------------------------------------------------------------------------
# 内部辅助函数
# ---------------------------------------------------------------------------


def _ensure_migrations_table(conn: "psycopg.Connection") -> None:  # type: ignore[name-defined]
    """如果不存在，则创建 schema_migrations 跟踪表。"""
    with conn.cursor() as cur:
        cur.execute(CREATE_SCHEMA_MIGRATIONS_TABLE_SQL)


def _get_applied_versions(conn: "psycopg.Connection") -> List[int]:  # type: ignore[name-defined]
    """返回已应用的迁移版本号列表。"""
    with conn.cursor() as cur:
        cur.execute("SELECT version FROM schema_migrations ORDER BY version")
        rows = cur.fetchall()
    return [int(row[0]) for row in rows]


def _record_migration(conn: "psycopg.Connection", version: int) -> None:  # type: ignore[name-defined]
    """向 schema_migrations 插入版本记录。"""
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO schema_migrations (version) VALUES (%s) ON CONFLICT DO NOTHING",
            (version,),
        )


def _apply_parts(conn: "psycopg.Connection", parts: "tuple[str, ...]") -> None:  # type: ignore[name-defined]
    """使用提供的连接逐个执行每个 SQL 部分。

    psycopg v3 将每个 ``execute()`` 调用作为单个查询发送，因此
    多语句字符串必须在调用此函数之前拆分为单独的部分。
    """
    with conn.cursor() as cur:
        for part in parts:
            sql = part.strip()
            if sql:
                cur.execute(sql)


# ---------------------------------------------------------------------------
# 公共 API
# ---------------------------------------------------------------------------


def run_migrations() -> None:
    """按顺序应用所有待处理的版本化迁移。

    算法
    ---------
    1. 为整个迁移运行打开单个连接。
    2. 确保 ``schema_migrations`` 跟踪表存在。
    3. 获取已应用的版本号。
    4. 对于 ``MIGRATIONS`` 中的每个迁移 ``(version, sql_parts)``，如果
       其版本已被记录则跳过；否则按顺序执行每个 SQL 部分并记录
       版本 —— 全部在 psycopg v3 在上下文管理器退出时提交的同一
       自动提交风格事务中完成。
    """
    with get_db_connection() as conn:
        _ensure_migrations_table(conn)
        applied = set(_get_applied_versions(conn))

        for version, sql_parts in MIGRATIONS:
            if version in applied:
                continue
            _apply_parts(conn, sql_parts)
            _record_migration(conn, version)


def ensure_users_table_exists() -> None:
    """兼容性适配：如果不存在则创建 user_info 表。

    建议优先调用 :func:`run_migrations`，它处理完整的版本化 schema。
    保留此函数是为了使现有调用点无需修改即可继续工作。
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_USERS_TABLE_SQL)


def init_schema(ddls: "Iterable[str] | None" = None) -> None:  # type: ignore[name-defined]
    """初始化数据库 schema。

    当 *ddls* 为 ``None`` 时使用版本化迁移运行器。
    当提供显式的 DDL 字符串可迭代对象时，直接应用每个 DDL
    （遗留行为，在测试中很有用）。

    Args:
        ddls: 可选的原始 DDL 字符串可迭代对象。传入 ``None`` 则运行
              完整的版本化迁移套件。
    """
    if ddls is None:
        run_migrations()
        return

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for sql in ddls:
                cur.execute(sql)
