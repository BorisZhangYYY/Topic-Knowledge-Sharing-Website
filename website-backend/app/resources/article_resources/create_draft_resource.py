from __future__ import annotations

from typing import Any, Dict, Tuple


from flask import g, request
from flask_restful import Resource

from app.auth.middleware import require_auth

from app.db.connection import get_db_connection
from app.db.article_info_model import ArticleInfo

from datetime import datetime, timezone


class CreateDraftResource(Resource):
    """创建文章草稿资源。

    说明:
        POST /api/articles/drafts

    请求体:
        - title (str, optional): 草稿标题，可为空字符串，缺省时使用默认标题。

    返回:
        201 成功，返回草稿基础信息，包含 id、author_id、author_name、title 等字段。
    """

    @require_auth
    def post(self) -> Tuple[Dict[str, Any], int]:
        """创建新的文章草稿。

        Returns:
            Tuple[Dict[str, Any], int]: 返回响应体与 HTTP 状态码。
        """
        payload: Any = request.get_json(silent=True)
        # 请求体为空时视为无字段输入，统一落到默认值逻辑。
        if payload is None:
            payload = {}
        if not isinstance(payload, dict):
            return {"message": "validation_error", "errors": {"payload": "需要是 dict 对象"}}, 400

        # ------------------------------------------------------------------
        # 1. 处理字段放入draft对象
        # ------------------------------------------------------------------
        # 防止非字符串 title 造成后续处理异常。
        title_raw: Any = payload.get("title", "")
        if title_raw is not None and not isinstance(title_raw, str):
            return {"message": "validation_error", "errors": {"title": "标题必须是字符串"}}, 400
        title: str = (title_raw or "").strip()
        if title == "":
            title = "Untitled"

        # 认证信息来自中间件写入的 g.current_user。
        author_ctx: Any = getattr(g, "current_user", {})
        author_name: str = author_ctx.get("username", "") if isinstance(author_ctx, dict) else ""
        author_id_raw: Any = author_ctx.get("user_id") if isinstance(author_ctx, dict) else None
        # user_id 需要转换为整数，失败直接视为未授权。
        try:
            author_id: int = int(author_id_raw)
        except Exception:
            return {"message": "unauthorized"}, 401
        if author_name == "":
            return {"message": "unauthorized"}, 401

        now: datetime = datetime.now(timezone.utc)
        draft = {
            "author_id": author_id,
            "title": title.strip(),
            "author_name": author_name,
            "status": "draft",
            "markdown_source": "",
            "version": 1,
            "created_at": now,
            "updated_at": now,
        }
        
        # ------------------------------------------------------------------
        # 2. 创建草稿并入库
        # ------------------------------------------------------------------
        try:
            with get_db_connection() as conn:
                with conn.transaction():
                    with conn.cursor() as cur:
                        cur.execute(
                            f"""
                            INSERT INTO {ArticleInfo.TABLE_NAME}
                            (author_id, author_name, title, status, markdown_source, version, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id
                            """,
                            (draft["author_id"], draft["author_name"], draft["title"], draft["status"], draft["markdown_source"], 
                             draft["version"], draft["created_at"], draft["updated_at"]),
                        )
                        row = cur.fetchone()
                        if row is None:
                            return {"message": "database_error", "detail": "insert_draft_failed"}, 500
                        
                        draft["id"] = int(row[0]) # 从数据库返回的 ID 为整数类型
                        
        except Exception as exc:
            return {"message": "database_error", "detail": str(exc)}, 500

        # ------------------------------------------------------------------
        # 3. 返回响应
        # ------------------------------------------------------------------
        draft["created_at"] = draft["created_at"].isoformat()
        draft["updated_at"] = draft["updated_at"].isoformat()
        return {"message": "ok", "draft": draft}, 201
