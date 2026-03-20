from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar


@dataclass(frozen=True)
class ArticleInfo:
    """article_info 表数据模型。"""

    TABLE_NAME: ClassVar[str] = "article_info"

    id: int
    author_id: int
    title: str
    author_name: str
    status: str
    markdown_source: str
    version: int
    created_at: datetime
    updated_at: datetime
