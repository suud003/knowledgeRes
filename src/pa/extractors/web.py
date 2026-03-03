"""通用 Web 内容提取器.

使用 trafilatura 进行智能正文提取，bs4 解析元数据。
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from pa.extractors.base import BaseExtractor
from pa.extractors.models import ExtractedContent, ExtractedImage

# 延迟导入可选依赖
trafilatura = None
BeautifulSoup = None


def _import_deps() -> None:
    global trafilatura, BeautifulSoup
    if trafilatura is None:
        try:
            import trafilatura as _trafilatura
            trafilatura = _trafilatura
        except ImportError:
            pass
    if BeautifulSoup is None:
        try:
            from bs4 import BeautifulSoup as _BS
            BeautifulSoup = _BS
        except ImportError:
            pass


class WebExtractor(BaseExtractor):
    """通用网页内容提取器."""
    
    name = "web"
    supported_domains = []  # 空列表表示处理所有站点
    
    async def extract(self, url: str, html: str) -> ExtractedContent:
        """从 HTML 提取内容."""
        _import_deps()
        
        title = ""
        content = ""
        author = ""
        publish_date = ""
        site_name = ""
        cover_image = ""
        
        # 使用 trafilatura 提取正文
        if trafilatura:
            content = trafilatura.extract(
                html,
                include_images=True,
                include_links=True,
                output_format="markdown",
                favor_precision=True,
            ) or ""
            
            # 提取元数据
            metadata = trafilatura.extract_metadata(html)
            if metadata:
                title = metadata.title or ""
                author = metadata.author or ""
                publish_date = metadata.date or ""
                site_name = metadata.sitename or ""
        
        # 使用 bs4 补充元数据
        if BeautifulSoup:
            soup = BeautifulSoup(html, "html.parser")
            
            if not title:
                title = self._extract_title(soup)
            if not author:
                author = self._extract_author(soup)
            if not publish_date:
                publish_date = self._extract_date(soup)
            if not site_name:
                site_name = self._extract_site_name(soup, url)
            cover_image = self._extract_cover_image(soup)
            
            # 如果 trafilatura 失败，尝试简单提取
            if not content:
                content = self._simple_extract(soup)
        
        # 提取图片
        images = self.extract_images_from_content(content)
        
        return ExtractedContent(
            title=title,
            content=content,
            url=url,
            author=author,
            publish_date=publish_date,
            site_name=site_name,
            site_type=self._detect_site_type(url),
            images=images,
            cover_image=cover_image,
            extractor_name=self.name,
        )
    
    def _extract_title(self, soup: Any) -> str:
        """提取标题."""
        # 优先级: og:title > title > h1
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]
        
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text().strip()
        
        h1 = soup.find("h1")
        if h1:
            return h1.get_text().strip()
        
        return ""
    
    def _extract_author(self, soup: Any) -> str:
        """提取作者."""
        selectors = [
            ("meta", {"name": "author"}),
            ("meta", {"property": "article:author"}),
            ("a", {"rel": "author"}),
            ("span", {"class": re.compile(r"author|byline", re.I)}),
        ]
        for tag, attrs in selectors:
            el = soup.find(tag, attrs)
            if el:
                return el.get("content", "") or el.get_text().strip()
        return ""
    
    def _extract_date(self, soup: Any) -> str:
        """提取发布日期."""
        selectors = [
            ("meta", {"property": "article:published_time"}),
            ("meta", {"name": "pubdate"}),
            ("time", {"datetime": True}),
        ]
        for tag, attrs in selectors:
            el = soup.find(tag, attrs)
            if el:
                return el.get("content", "") or el.get("datetime", "")
        return ""
    
    def _extract_site_name(self, soup: Any, url: str) -> str:
        """提取站点名称."""
        og_site = soup.find("meta", property="og:site_name")
        if og_site and og_site.get("content"):
            return og_site["content"]
        return urlparse(url).netloc
    
    def _extract_cover_image(self, soup: Any) -> str:
        """提取封面图."""
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"]
        return ""
    
    def _simple_extract(self, soup: Any) -> str:
        """简单正文提取 (fallback)."""
        # 移除脚本和样式
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        
        # 尝试找 article 或 main
        article = soup.find("article") or soup.find("main")
        if article:
            return article.get_text(separator="\n\n", strip=True)
        
        # 最后用 body
        body = soup.find("body")
        if body:
            return body.get_text(separator="\n\n", strip=True)[:5000]
        
        return ""
    
    def _detect_site_type(self, url: str) -> str:
        """检测站点类型."""
        domain = urlparse(url).netloc.lower()
        
        type_map = {
            "mp.weixin.qq.com": "wechat",
            "weixin.qq.com": "wechat",
            "zhihu.com": "zhihu",
            "juejin.cn": "juejin",
            "juejin.im": "juejin",
            "github.com": "github",
            "medium.com": "medium",
            "twitter.com": "twitter",
            "x.com": "twitter",
        }
        
        for key, site_type in type_map.items():
            if key in domain:
                return site_type
        
        return "articles"
