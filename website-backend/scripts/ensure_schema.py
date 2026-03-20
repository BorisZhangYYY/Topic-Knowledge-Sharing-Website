from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def main() -> int:
    """执行核心表建表脚本。

    Args:
        无。

    Returns:
        退出码。
    """
    from run import app
    from app.db.schema import ensure_core_tables

    with app.app_context():
        ensure_core_tables()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
