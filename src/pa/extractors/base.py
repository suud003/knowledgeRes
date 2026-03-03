"""提取器基类."""

from __future__ import annotations

import hashlib
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pa.extractors.models import ExtractedContent, ExtractedImage


class BaseExtractor(ABC):
    """内容提取器基类."""
    
    name: str = "base"
    supported_domains: list[str] = []
    
    def __init__(self, assets_dir: Path | None = None) -> None:
        self.assets_dir = assets_dir or Path("data/assets/images")
        self.assets_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    async def extract(self, url: str, html: str) -> ExtractedContent:
        """从 HTML 提取内容."""
        pass
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        """判断是否能处理该 URL."""
        domain = urlparse(url).netloc
        return any(d in domain for d in cls.supported_domains)
    
    def extract_images_from_content(self, content: str) -> list[ExtractedImage]:
        """从 Markdown 内容中提取图片."""
        images = []
        pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        for match in re.finditer(pattern, content):
            alt_text, url = match.groups()
            images.append(ExtractedImage(original_url=url, alt_text=alt_text))
        return images
    
    def generate_image_filename(self, url: str, index: int = 0) -> str:
        """生成本地图片文件名."""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        ext = Path(urlparse(url).path).suffix or ".jpg"
        return f"img_{url_hash}_{index}{ext}"
    
    def replace_images_in_content(
        self, content: str, image_map: dict[str, str]
    ) -> str:
        """替换内容中的图片 URL 为本地路径."""
        for original_url, local_path in image_map.items():
            content = content.replace(original_url, local_path)
        return content
