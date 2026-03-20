"""
init_db.py - 数据库初始化助手

将目标数据库重置为干净状态，重新创建核心表，
并创建一个默认管理员用户。

使用方式
--------
    # 使用 conf/global.conf 默认值（推荐）
    python website-backend/scripts/init_db.py

    # 覆盖特定字段
    python website-backend/scripts/init_db.py \
        --conf website-backend/conf/global.conf \
        --admin-username admin \
        --admin-password Admin1234! \
        --admin-email admin@example.com

    # 试运行：显示将要执行的操作而不实际执行
    python website-backend/scripts/init_db.py --dry-run

执行步骤
--------
1. 连接到 global.conf 中定义的数据库（或通过 CLI 参数指定）。
2. 在操作之前自动备份快照到 backups/ 目录。
3. 删除所有应用表（user_info, article_info），重新开始。
4. 通过 app.db.schema 重新创建核心表结构。
5. 创建一个默认管理员用户（用户名/密码/邮箱可配置）。
6. 打印执行摘要。

安全性
------
- 需要显式的 --yes 标志（或交互式确认）以防止
  在生产环境中意外丢失数据。
- 始终首先创建备份快照（使用 pg_snapshot.py 逻辑）。
- 从不硬编码凭据；从配置文件或环境变量读取。
"""
from __future__ import annotations

import argparse
import os
import sys
from configparser import ConfigParser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
from app.db.schema import SCHEMA_TABLES  # type: ignore[import]

# ---------------------------------------------------------------------------
# 确保后端根目录在 sys.path 中，以便我们可以从项目根目录运行脚本时
# 导入应用模块。
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent          # scripts/
BACKEND_DIR = SCRIPT_DIR.parent                        # website-backend/
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# ---------------------------------------------------------------------------
# 配置加载（采用与 pg_snapshot.py 相同的方法）
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PgConfig:
    host: str
    port: int
    user: str
    password: str
    db: str


def _read_conf(conf_path: Path) -> dict[str, str]:
    if not conf_path.exists():
        return {}
    parser = ConfigParser()
    parser.read(conf_path)
    if not parser.has_section("postgres"):
        return {}
    return {k: v for k, v in parser.items("postgres")}


def load_pg_config(
    conf_path: Path,
    host: Optional[str] = None,
    port: Optional[int] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    db: Optional[str] = None,
) -> PgConfig:
    data = _read_conf(conf_path)
    return PgConfig(
        host=host     or data.get("host")     or os.getenv("POSTGRES_HOST", "localhost"),
        port=port     or int(data.get("port") or os.getenv("POSTGRES_PORT", "5432")),
        user=user     or data.get("user")     or os.getenv("POSTGRES_USER", "postgres"),
        password=password or data.get("password") or os.getenv("POSTGRES_PASSWORD", ""),
        db=db         or data.get("db")       or os.getenv("POSTGRES_DB", "postgres"),
    )


# ---------------------------------------------------------------------------
# 快照助手（复用 pg_snapshot.export_db）
# ---------------------------------------------------------------------------

def _take_backup(cfg: PgConfig, backup_dir: Path) -> Path:
    """在操作之前导出完整的 SQL 快照。"""
    # 在此处导入，以便即使 pg_snapshot 有问题，脚本仍然可以运行
    from scripts.pg_snapshot import export_db, PgConfig as SnapshotCfg  # type: ignore[import]

    snap_cfg = SnapshotCfg(
        host=cfg.host,
        port=cfg.port,
        user=cfg.user,
        password=cfg.password,
        db=cfg.db,
    )
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = backup_dir / f"{cfg.db}-before-init-{ts}.sql"
    backup_dir.mkdir(parents=True, exist_ok=True)
    export_db(snap_cfg, out)
    return out


# ---------------------------------------------------------------------------
# 核心重置 + 种子逻辑
# ---------------------------------------------------------------------------

def _build_drop_tables_sql() -> str:
    """根据 schema 中的表定义构建 drop 语句。"""

    lines = [f"DROP TABLE IF EXISTS {table.table_name} CASCADE;" for table in reversed(SCHEMA_TABLES)] # 倒序删除，防止外键依赖问题报错
    return "\n".join(lines)


def _reset_schema(dsn: str, dry_run: bool) -> None:
    """删除所有应用表，使重建从零开始。"""

    drop_tables_sql = _build_drop_tables_sql()
    table_names = ", ".join(table.table_name for table in SCHEMA_TABLES)
    print(f"[init] Dropping existing tables ({table_names})…")
    if dry_run:
        print(f"[dry-run] Would execute:\n{drop_tables_sql.strip()}")
        return
    import psycopg  # type: ignore[import]

    with psycopg.connect(dsn, connect_timeout=5) as conn:
        with conn.cursor() as cur:
            cur.execute(drop_tables_sql)
    print("[init] Tables dropped.")


def _ensure_schema(dry_run: bool) -> None:
    """通过应用的 schema 模块确保核心表存在。"""
    print("[init] Ensuring core tables…")
    if dry_run:
        print("[dry-run] Would call ensure_core_tables() — skipped.")
        return

    # 需要 Flask 应用上下文，因为 get_db_connection() 读取 current_app.config
    from run import app  # type: ignore[import]
    from app.db.schema import ensure_core_tables  # type: ignore[import]

    with app.app_context():
        ensure_core_tables()
    print("[init] Core tables are ready.")


def _seed_admin(
    dsn: str,
    username: str,
    password: str,
    email: str,
    dry_run: bool,
) -> None:
    """插入默认管理员用户。"""
    from app.auth.passwords import hash_password  # type: ignore[import]
    from app.auth.validation import validate_username, validate_password, validate_email  # type: ignore[import]

    # 在操作数据库之前验证输入
    ok, msg = validate_username(username)
    if not ok:
        print(f"[error] Invalid admin username: {msg}")
        sys.exit(1)

    ok, msg = validate_password(password)
    if not ok:
        print(f"[error] Invalid admin password: {msg}")
        sys.exit(1)

    ok, msg = validate_email(email)
    if not ok:
        print(f"[error] Invalid admin email: {msg}")
        sys.exit(1)

    pw_hash = hash_password(password)

    insert_sql = """
    INSERT INTO user_info (username, password_hash, email, is_active, email_verified)
    VALUES (%s, %s, %s, TRUE, TRUE)
    RETURNING id;
    """

    print(f"[init] Seeding default admin user '{username}' <{email}>…")
    if dry_run:
        print(f"[dry-run] Would insert admin user '{username}' — skipped.")
        return
    import psycopg  # type: ignore[import]

    with psycopg.connect(dsn, connect_timeout=5) as conn:
        with conn.cursor() as cur:
            cur.execute(insert_sql, (username, pw_hash, email))
            row = cur.fetchone()
    user_id = int(row[0]) if row else "?"
    print(f"[init] Admin user created  →  id={user_id}  username={username}  email={email}")


# ---------------------------------------------------------------------------
# 命令行接口
# ---------------------------------------------------------------------------

DEFAULT_CONF = BACKEND_DIR / "conf" / "global.conf"
DEFAULT_BACKUP_DIR = BACKEND_DIR / "backups"

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "Admin1234!"
DEFAULT_ADMIN_EMAIL    = "admin@example.com"


def _confirm(prompt: str) -> bool:
    try:
        answer = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return answer in ("y", "yes")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="init_db",
        description="重置数据库，重建核心表，并创建默认管理员用户。",
    )
    parser.add_argument("--conf",     default=str(DEFAULT_CONF), help="Path to global.conf")
    parser.add_argument("--host",     default=None)
    parser.add_argument("--port",     type=int, default=None)
    parser.add_argument("--user",     default=None, help="DB role / superuser for connection")
    parser.add_argument("--password", default=None)
    parser.add_argument("--db",       default=None, help="Target database name")

    parser.add_argument("--admin-username", default=DEFAULT_ADMIN_USERNAME)
    parser.add_argument("--admin-password", default=DEFAULT_ADMIN_PASSWORD)
    parser.add_argument("--admin-email",    default=DEFAULT_ADMIN_EMAIL)

    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip the automatic pre-reset backup snapshot",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making any changes",
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip interactive confirmation prompt",
    )

    args = parser.parse_args()

    cfg = load_pg_config(
        conf_path=Path(args.conf),
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        db=args.db,
    )

    # 构建 psycopg DSN 字符串
    auth = f"{cfg.user}:{cfg.password}@" if cfg.password else f"{cfg.user}@"
    dsn = f"postgresql://{auth}{cfg.host}:{cfg.port}/{cfg.db}"

    # ── 摘要横幅 ──────────────────────────────────────────────────────
    print("=" * 60)
    print("  init_db — Database Reset & Seed")
    print("=" * 60)
    print(f"  Target   : {cfg.db} @ {cfg.host}:{cfg.port}")
    print(f"  DB user  : {cfg.user}")
    print(f"  Admin    : {args.admin_username} <{args.admin_email}>")
    print(f"  Backup   : {'SKIPPED (--no-backup)' if args.no_backup else str(DEFAULT_BACKUP_DIR)}")
    print(f"  Dry-run  : {args.dry_run}")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This will DROP all existing data in the database.")
    print()

    if not args.dry_run and not args.yes:
        if not _confirm("Type 'yes' to continue, anything else to abort: "):
            print("[aborted] No changes were made.")
            return 0

    # ── 步骤 1：备份 ──────────────────────────────────────────────────────
    if not args.no_backup and not args.dry_run:
        print("[init] Taking backup snapshot before reset…")
        try:
            snap_path = _take_backup(cfg, DEFAULT_BACKUP_DIR)
            print(f"[init] Backup saved → {snap_path}")
        except Exception as exc:
            print(f"[warning] Backup failed ({exc}). Continuing anyway.")
    else:
        if args.dry_run:
            print("[dry-run] Would take backup snapshot — skipped.")

    # ── 步骤 2：删除表 ─────────────────────────────────────────────────
    _reset_schema(dsn, dry_run=args.dry_run)

    # ── 步骤 3：重建核心表 ─────────────────────────────────────────────
    _ensure_schema(dry_run=args.dry_run)

    # ── 步骤 4：创建管理员用户 ─────────────────────────────────────────────
    _seed_admin(
        dsn=dsn,
        username=args.admin_username,
        password=args.admin_password,
        email=args.admin_email,
        dry_run=args.dry_run,
    )

    # ── 完成 ────────────────────────────────────────────────────────────────
    print()
    print("=" * 60)
    if args.dry_run:
        print("  [dry-run complete] No changes were made.")
    else:
        print("  ✅  Database initialised successfully.")
        print()
        print(f"  Default admin credentials:")
        print(f"    Username : {args.admin_username}")
        print(f"    Password : {args.admin_password}")
        print(f"    Email    : {args.admin_email}")
        print()
        print("  ⚠️  Change the admin password after first login!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
