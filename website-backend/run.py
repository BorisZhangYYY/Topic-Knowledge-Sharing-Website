from __future__ import annotations

import os
from typing import Any, Dict, Tuple

from flask import Flask, Response, jsonify

from conf.config import Config
from app.common_func.api import create_api

import psycopg

app = Flask(__name__) # 创建Flask应用实例
app.config.from_object(Config()) # 导入配置类Config的配置项
create_api(app) # 创建API路由

def create_app() -> Flask:
    """创建并配置 Flask 应用。

    Returns:
        配置好的 Flask 应用实例。
    """
    return app

@app.get("/")
def index() -> Response:
    """返回基本应用信息。"""
    payload: Dict[str, Any] = {
        "app": "Noosphere-backend",
        "debug": app.config.get("DEBUG", False),
        "database_dsn": app.config.get("DATABASE_DSN", ""),
    }
    return jsonify(payload)


@app.get("/healthz")
def healthz() -> Response:
    """返回应用健康状态。"""
    payload: Dict[str, str] = {"status": "ok"}
    return jsonify(payload)

def _db_connect() -> "psycopg.Connection[Any]":  # type: ignore[name-defined]
    """使用配置的 DSN 创建新的数据库连接。"""
    if psycopg is None:
        raise RuntimeError("psycopg is not installed")
    dsn = str(app.config.get("DATABASE_DSN", ""))
    return psycopg.connect(dsn, connect_timeout=3)

@app.get("/db/health")
def db_health() -> Response:
    """使用 SELECT 1 执行简单的 PostgreSQL 健康检查。"""
    try:
        with _db_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                row: Tuple[int] = cur.fetchone()  # type: ignore[assignment]
        status: Dict[str, Any] = {"database": "ok", "result": int(row[0])}
        return jsonify(status)
    except Exception as exc:  # pragma: no cover
        status = {"database": "error", "detail": str(exc)}
        return jsonify(status), 503

if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", "15000"))
    app.run(host=host, port=port, debug=app.config.get("DEBUG", False))
