from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from app.db.article_info_model import ArticleInfo
from app.db.connection import get_db_connection
from app.db.user_info_model import UserInfo


@dataclass(frozen=True)
class TableSchema:
    """单表 schema 定义。"""

    model: type[object]
    table_name: str
    create_sql: str
    index_sqls: tuple[str, ...]
    alter_sqls: tuple[str, ...] = ()

# 无外键依赖：可以任意顺序填写入TableSchema。
# 有外键依赖：把“被依赖的表”写前面，把“依赖它的表”写后面。
SCHEMA_TABLES: Final[tuple[TableSchema, ...]] = (
    TableSchema(
        model=UserInfo,
        table_name=UserInfo.TABLE_NAME,
        create_sql="""
CREATE TABLE IF NOT EXISTS user_info (
    id               BIGSERIAL    PRIMARY KEY,
    username         TEXT         UNIQUE NOT NULL,
    password_hash    TEXT         NOT NULL,
    email            TEXT         UNIQUE,
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE,
    email_verified   BOOLEAN      NOT NULL DEFAULT FALSE,
    last_login_at    TIMESTAMPTZ,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
)
""",
        index_sqls=(
            "CREATE INDEX IF NOT EXISTS idx_user_info_username ON user_info (username)",
            "CREATE INDEX IF NOT EXISTS idx_user_info_email ON user_info (email)",
        ),
    ),
    TableSchema(
        model=ArticleInfo,
        table_name=ArticleInfo.TABLE_NAME,
        create_sql="""
CREATE TABLE IF NOT EXISTS article_info (
    id               BIGSERIAL    PRIMARY KEY,
    author_id        BIGINT       NOT NULL REFERENCES user_info(id) ON DELETE CASCADE,
    author_name      TEXT         NOT NULL DEFAULT '',
    title            TEXT         NOT NULL DEFAULT '',
    status           TEXT         NOT NULL DEFAULT 'draft',
    markdown_source  TEXT         NOT NULL DEFAULT '',
    version          INT          NOT NULL DEFAULT 1,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
)
""",
        index_sqls=(
            "CREATE INDEX IF NOT EXISTS idx_article_info_author_id ON article_info (author_id)",
            "CREATE INDEX IF NOT EXISTS idx_article_info_status ON article_info (status)",
        ),
    ),
)


def _collect_core_schema_ddls() -> tuple[str, ...]:
    """收集需要执行的建表和增量变更 SQL。"""
    merged: list[str] = []
    for table_schema in SCHEMA_TABLES:
        merged.append(table_schema.create_sql)
        merged.extend(table_schema.index_sqls)
        merged.extend(table_schema.alter_sqls)
    return tuple(merged)


def ensure_core_tables() -> None:
    """确保项目核心表存在。"""
    core_schema_ddls = _collect_core_schema_ddls()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for sql in core_schema_ddls:
                cur.execute(sql)


def main() -> int:
    """执行核心表建表入口。

    Args:
        无。

    Returns:
        退出码。
    """
    from run import app

    with app.app_context():
        ensure_core_tables()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
