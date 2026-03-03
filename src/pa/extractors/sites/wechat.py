"""微信公众号内容提取器."""

from __future__ import annotations

import re
from typing import Any

from pa.extractors.base import BaseExtractor
from pa.extractors.models import ExtractedContent, ExtractedImage

BeautifulSoup = None


def _import_bs4() -> None:
    global BeautifulSoup
    if BeautifulSoup is None:
        try:
            from bs4 import BeautifulSoup as _BS
            BeautifulSoup = _BS
        except ImportError:
            pass


class WechatExtractor(BaseExtractor):
    """微信公众号文章提取器."""
    
    name = "wechat"
    supported_domains = ["mp.weixin.qq.com", "weixin.qq.com"]
    
    async def extract(self, url: str, html: str) -> ExtractedContent:
        """从微信公众号文章提取内容."""
        _import_bs4()
        
        if not BeautifulSoup:
            raise ImportError("需要安装 beautifulsoup4")
        
        soup = BeautifulSoup(html, "html.parser")
        
        # 提取标题
        title = self._extract_title(soup)
        
        # 提取公众号名称和作者
        account_name, author = self._extract_author_info(soup)
        
        # 提取发布时间
        publish_date = self._extract_date(soup)
        
        # 提取正文
        content = self._extract_content(soup)
        
        # 提取图片
        images = self._extract_images(soup)
        
        # 提取封面图
        cover_image = self._extract_cover(soup)
        
        return ExtractedContent(
            title=title,
            content=content,
            url=url,
            author=author or account_name,
            publish_date=publish_date,
            site_name=account_name or "微信公众号",
            site_type="wechat",
            images=images,
            cover_image=cover_image,
            extractor_name=self.name,
        )
    
    def _extract_title(self, soup: Any) -> str:
        """提取文章标题."""
        # 微信标题在 h1#activity-name 或 meta og:title
        h1 = soup.find("h1", id="activity-name")
        if h1:
            return h1.get_text().strip()
        
        og_title = soup.find("meta", property="og:title")
        if og_title:
            return og_title.get("content", "")
        
        return ""
    
    def _extract_author_info(self, soup: Any) -> tuple[str, str]:
        """提取公众号名称和作者."""
        account_name = ""
        author = ""
        
        # 公众号名称
        account_el = soup.find("a", id="js_name") or soup.find("span", class_="profile_nickname")
        if account_el:
            account_name = account_el.get_text().strip()
        
        # 作者 (如果有)
        author_el = soup.find("span", class_="rich_media_meta_text")
        if author_el:
            author = author_el.get_text().strip()
        
        return account_name, author
    
    def _extract_date(self, soup: Any) -> str:
        """提取发布日期."""
        # 尝试从 script 中提取
        scripts = soup.find_all("script")
        for script in scripts:
            text = script.string or ""
            match = re.search(r'var publish_time\s*=\s*"([^"]+)"', text)
            if match:
                return match.group(1)
        
        # 或者从 em#publish_time
        em = soup.find("em", id="publish_time")
        if em:
            return em.get_text().strip()
        
        return ""
    
    def _extract_content(self, soup: Any) -> str:
        """提取正文内容."""
        # 微信正文在 div#js_content
        content_div = soup.find("div", id="js_content")
        if not content_div:
            return ""
        
        # 转换为 Markdown
        lines = []
        for el in content_div.descendants:
            if el.name == "p":
                text = el.get_text().strip()
                if text:
                    lines.append(text + "\n")
            elif el.name in ["h1", "h2", "h3", "h4"]:
                level = int(el.name[1])
                text = el.get_text().strip()
                if text:
                    lines.append("#" * level + " " + text + "\n")
            elif el.name == "img":
                src = el.get("data-src") or el.get("src", "")
                alt = el.get("alt", "")
                if src:
                    lines.append(f"![{alt}]({src})\n")
            elif el.name == "blockquote":
                text = el.get_text().strip()
                if text:
                    lines.append("> " + text.replace("\n", "\n> ") + "\n")
        
        return "\n".join(lines)
    
    def _extract_images(self, soup: Any) -> list[ExtractedImage]:
        """提取文章图片."""
        images = []
        content_div = soup.find("div", id="js_content")
        if content_div:
            for img in content_div.find_all("img"):
                src = img.get("data-src") or img.get("src", "")
                if src and not src.startswith("data:"):
                    images.append(ExtractedImage(
                        original_url=src,
                        alt_text=img.get("alt", ""),
                    ))
        return images
    
    def _extract_cover(self, soup: Any) -> str:
        """提取封面图."""
        og_image = soup.find("meta", property="og:image")
        if og_image:
            return og_image.get("content", "")
        return ""
