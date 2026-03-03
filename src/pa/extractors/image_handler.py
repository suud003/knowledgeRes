"""图片本地化处理模块.

负责下载网页中的图片并保存到本地，替换内容中的远程 URL。
"""

from __future__ import annotations

import asyncio
import hashlib
import mimetypes
import re
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse, urljoin

if TYPE_CHECKING:
    from pa.extractors.models import ExtractedImage

# 延迟导入
httpx = None


def _import_httpx() -> None:
    global httpx
    if httpx is None:
        try:
            import httpx as _httpx
            httpx = _httpx
        except ImportError:
            pass


class ImageHandler:
    """图片本地化处理器."""
    
    # 支持的图片格式
    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
    
    # 默认请求头
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    }
    
    def __init__(
        self,
        assets_dir: Path | str,
        base_url: str = "",
        max_concurrent: int = 5,
        timeout: float = 30.0,
    ) -> None:
        """初始化图片处理器.
        
        Args:
            assets_dir: 图片保存目录
            base_url: 用于解析相对路径的基础 URL
            max_concurrent: 最大并发下载数
            timeout: 下载超时时间(秒)
        """
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = base_url
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_content(
        self,
        content: str,
        source_url: str = "",
    ) -> tuple[str, list[dict]]:
        """处理内容中的图片，下载并替换 URL.
        
        Args:
            content: Markdown 内容
            source_url: 来源 URL (用于解析相对路径)
        
        Returns:
            (处理后的内容, 图片信息列表)
        """
        _import_httpx()
        
        if not httpx:
            return content, []
        
        # 提取所有图片 URL
        image_urls = self._extract_image_urls(content)
        
        if not image_urls:
            return content, []
        
        # 下载所有图片
        base = source_url or self.base_url
        download_results = await self._download_all(image_urls, base)
        
        # 替换内容中的 URL
        processed_content = content
        image_infos = []
        
        for original_url, result in download_results.items():
            if result["success"]:
                local_path = result["local_path"]
                # 使用相对路径
                relative_path = self._get_relative_path(local_path)
                processed_content = processed_content.replace(original_url, relative_path)
                image_infos.append({
                    "original_url": original_url,
                    "local_path": str(local_path),
                    "relative_path": relative_path,
                    "size": result.get("size", 0),
                })
        
        return processed_content, image_infos
    
    def _extract_image_urls(self, content: str) -> list[str]:
        """从 Markdown 内容提取图片 URL."""
        urls = []
        
        # Markdown 图片: ![alt](url)
        md_pattern = r'!\[[^\]]*\]\(([^)]+)\)'
        for match in re.finditer(md_pattern, content):
            url = match.group(1).strip()
            if url and not url.startswith("data:"):
                urls.append(url)
        
        # HTML 图片: <img src="url">
        html_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        for match in re.finditer(html_pattern, content, re.I):
            url = match.group(1).strip()
            if url and not url.startswith("data:"):
                urls.append(url)
        
        return list(set(urls))  # 去重
    
    async def _download_all(
        self,
        urls: list[str],
        base_url: str,
    ) -> dict[str, dict]:
        """并发下载所有图片."""
        tasks = []
        for url in urls:
            # 解析相对 URL
            full_url = urljoin(base_url, url) if base_url and not url.startswith("http") else url
            tasks.append(self._download_one(url, full_url))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            url: (result if isinstance(result, dict) else {"success": False, "error": str(result)})
            for url, result in zip(urls, results)
        }
    
    async def _download_one(self, original_url: str, full_url: str) -> dict:
        """下载单张图片."""
        async with self._semaphore:
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    follow_redirects=True,
                ) as client:
                    response = await client.get(full_url, headers=self.DEFAULT_HEADERS)
                    response.raise_for_status()
                    
                    # 确定文件扩展名
                    ext = self._get_extension(full_url, response)
                    
                    # 生成文件名
                    filename = self._generate_filename(full_url, ext)
                    local_path = self.assets_dir / filename
                    
                    # 保存文件
                    local_path.write_bytes(response.content)
                    
                    return {
                        "success": True,
                        "local_path": local_path,
                        "size": len(response.content),
                    }
            
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    def _get_extension(self, url: str, response: "httpx.Response") -> str:
        """获取图片扩展名."""
        # 优先从 Content-Type 获取
        content_type = response.headers.get("content-type", "")
        if content_type:
            ext = mimetypes.guess_extension(content_type.split(";")[0])
            if ext and ext in self.SUPPORTED_EXTENSIONS:
                return ext
        
        # 从 URL 获取
        parsed = urlparse(url)
        path_ext = Path(parsed.path).suffix.lower()
        if path_ext in self.SUPPORTED_EXTENSIONS:
            return path_ext
        
        return ".jpg"  # 默认
    
    def _generate_filename(self, url: str, ext: str) -> str:
        """生成本地文件名."""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        return f"img_{url_hash}{ext}"
    
    def _get_relative_path(self, local_path: Path) -> str:
        """获取相对于 assets 目录的路径."""
        # 返回 Obsidian 兼容的路径格式
        return f"assets/images/{local_path.name}"
    
    async def download_single(self, url: str) -> dict:
        """下载单张图片 (对外接口)."""
        _import_httpx()
        
        if not httpx:
            return {"success": False, "error": "httpx not installed"}
        
        return await self._download_one(url, url)
