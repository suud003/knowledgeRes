"""内容提取数据模型."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ExtractedImage:
    """提取的图片信息."""
    original_url: str
    local_path: str = ""
    alt_text: str = ""
    is_downloaded: bool = False


@dataclass
class ExtractedContent:
    """提取的网页内容统一数据模型."""
    
    title: str
    content: str
    url: str
    author: str = ""
    publish_date: str = ""
    site_name: str = ""
    site_type: str = "web"
    summary: str = ""
    tags: list[str] = field(default_factory=list)
    topic: str = ""
    images: list[ExtractedImage] = field(default_factory=list)
    cover_image: str = ""
    word_count: int = 0
    extracted_at: str = field(default_factory=lambda: datetime.now().isoformat())
    extractor_name: str = ""
    
    def __post_init__(self) -> None:
        if self.content and not self.word_count:
            chinese_chars = sum(1 for c in self.content if '\u4e00' <= c <= '\u9fff')
            self.word_count = chinese_chars + len(self.content.split()) // 2
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "author": self.author,
            "publish_date": self.publish_date,
            "site_name": self.site_name,
            "site_type": self.site_type,
            "summary": self.summary,
            "tags": self.tags,
            "topic": self.topic,
            "images": [{"url": img.original_url, "local": img.local_path} for img in self.images],
            "word_count": self.word_count,
        }
