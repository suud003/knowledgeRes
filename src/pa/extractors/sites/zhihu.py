"""知乎内容提取器."""

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


class ZhihuExtractor(BaseExtractor):
    """知乎文章/回答提取器."""
    
    name = "zhihu"
    supported_domains = ["zhihu.com", "zhuanlan.zhihu.com"]
    
    async def extract(self, url: str, html: str) -> ExtractedContent:
        """从知乎提取内容."""
        _import_bs4()
        
        if not BeautifulSoup:
            raise ImportError("需要安装 beautifulsoup4")
        
        soup = BeautifulSoup(html, "html.parser")
        
        # 判断是专栏文章还是问答
        is_zhuanlan = "zhuanlan.zhihu.com" in url
        
        if is_zhuanlan:
            return await self._extract_article(soup, url)
        else:
            return await self._extract_answer(soup, url)
    
    async def _extract_article(self, soup: Any, url: str) -> ExtractedContent:
        """提取专栏文章."""
        # 标题
        title = ""
        title_el = soup.find("h1", class_="Post-Title")
        if title_el:
            title = title_el.get_text().strip()
        
        # 作者
        author = ""
        author_el = soup.find("a", class_="UserLink-link")
        if author_el:
            author = author_el.get_text().strip()
        
        # 发布时间
        publish_date = ""
        time_el = soup.find("div", class_="ContentItem-time")
        if time_el:
            text = time_el.get_text()
            match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
            if match:
                publish_date = match.group(1)
        
        # 正文
        content = ""
        content_div = soup.find("div", class_="Post-RichText")
        if content_div:
            content = self._convert_to_markdown(content_div)
        
        # 图片
        images = self._extract_images(content_div) if content_div else []
        
        return ExtractedContent(
            title=title,
            content=content,
            url=url,
            author=author,
            publish_date=publish_date,
            site_name="知乎专栏",
            site_type="zhihu",
            images=images,
            extractor_name=self.name,
        )
    
    async def _extract_answer(self, soup: Any, url: str) -> ExtractedContent:
        """提取知乎回答."""
        # 问题标题
        title = ""
        title_el = soup.find("h1", class_="QuestionHeader-title")
        if title_el:
            title = title_el.get_text().strip()
        
        # 回答者
        author = ""
        author_el = soup.find("a", class_="UserLink-link")
        if author_el:
            author = author_el.get_text().strip()
        
        # 回答内容
        content = ""
        content_div = soup.find("div", class_="RichContent-inner")
        if content_div:
            content = self._convert_to_markdown(content_div)
        
        # 图片
        images = self._extract_images(content_div) if content_div else []
        
        return ExtractedContent(
            title=title,
            content=content,
            url=url,
            author=author,
            site_name="知乎",
            site_type="zhihu",
            images=images,
            extractor_name=self.name,
        )
    
    def _convert_to_markdown(self, element: Any) -> str:
        """将 HTML 元素转换为 Markdown."""
        lines = []
        
        for el in element.find_all(["p", "h1", "h2", "h3", "h4", "img", "blockquote", "ul", "ol"]):
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
                src = el.get("data-original") or el.get("src", "")
                alt = el.get("alt", "")
                if src and not src.startswith("data:"):
                    lines.append(f"![{alt}]({src})\n")
            elif el.name == "blockquote":
                text = el.get_text().strip()
                if text:
                    lines.append("> " + text.replace("\n", "\n> ") + "\n")
            elif el.name in ["ul", "ol"]:
                for li in el.find_all("li", recursive=False):
                    prefix = "- " if el.name == "ul" else "1. "
                    lines.append(prefix + li.get_text().strip() + "\n")
        
        return "\n".join(lines)
    
    def _extract_images(self, element: Any) -> list[ExtractedImage]:
        """提取图片."""
        images = []
        if element:
            for img in element.find_all("img"):
                src = img.get("data-original") or img.get("src", "")
                if src and not src.startswith("data:"):
                    images.append(ExtractedImage(
                        original_url=src,
                        alt_text=img.get("alt", ""),
                    ))
        return images
