"""RSS 采集器 - 自动订阅并抓取 RSS 源的最新文章."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import httpx

from pa.collectors.base import BaseCollector


def _get_proxy_for_url(url: str) -> str | None:
    """根据配置判断 URL 是否需要代理，返回代理地址或 None."""
    try:
        from pa.config import load_config
        config = load_config()
        return config.proxy.get_proxy_for_url(url)
    except Exception:
        return None


class RSSCollector(BaseCollector):
    """RSS 订阅采集器.

    支持 RSS 2.0 和 Atom 格式，可配置关键词过滤。
    """

    def __init__(
        self,
        name: str,
        raw_dir: Path,
        feed_url: str,
        topic: str = "reading",
        keywords: list[str] | None = None,
        max_articles: int = 10,
        days_back: int = 7,
    ) -> None:
        super().__init__(name, raw_dir)
        self.feed_url = feed_url
        self.topic = topic
        self.keywords = keywords or []
        self.max_articles = max_articles
        self.days_back = days_back
        # 已读文章记录文件，避免重复推送
        self.seen_file = self.raw_dir / f".{name}_seen.json"

    def get_source_type(self) -> str:
        return "rss"

    def _load_seen_ids(self) -> set[str]:
        """加载已推送过的文章 ID."""
        if self.seen_file.exists():
            try:
                with open(self.seen_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return set(data.get("ids", []))
            except Exception:
                return set()
        return set()

    def _save_seen_ids(self, ids: set[str]) -> None:
        """保存已推送过的文章 ID."""
        self.seen_file.parent.mkdir(parents=True, exist_ok=True)
        # 只保留最近 500 条记录
        id_list = list(ids)[-500:]
        with open(self.seen_file, "w", encoding="utf-8") as f:
            json.dump({"ids": id_list, "updated": datetime.now().isoformat()}, f)

    def _article_id(self, article: dict[str, Any]) -> str:
        """为文章生成唯一 ID."""
        key = f"{article.get('url', '')}{article.get('title', '')}"
        return hashlib.md5(key.encode()).hexdigest()

    async def collect(self) -> list[dict[str, Any]]:
        """抓取 RSS feed，返回新文章列表（自动去重已推送的）."""
        seen_ids = self._load_seen_ids()

        proxy = _get_proxy_for_url(self.feed_url)
        client_kwargs: dict[str, Any] = dict(timeout=4, follow_redirects=True)
        if proxy:
            client_kwargs["proxy"] = proxy
        async with httpx.AsyncClient(**client_kwargs) as client:
            resp = await client.get(self.feed_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            })
            resp.raise_for_status()

        # XML 解析容错：处理非标准 RSS 响应
        resp_text = resp.text.strip()
        if not resp_text or resp_text.startswith("<!DOCTYPE") or resp_text.startswith("<html"):
            raise ValueError(f"响应不是有效的 RSS/XML 格式（可能返回了 HTML 页面）")
        try:
            root = ElementTree.fromstring(resp_text)
        except ElementTree.ParseError as e:
            # 尝试清理常见的 XML 问题后重新解析
            import re
            cleaned = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#)', '&amp;', resp_text)
            try:
                root = ElementTree.fromstring(cleaned)
            except ElementTree.ParseError:
                raise ValueError(f"RSS XML 解析失败: {e}")

        # 兼容 RSS 2.0 和 Atom 格式
        items = root.findall(".//item") or root.findall(
            ".//{http://www.w3.org/2005/Atom}entry"
        )

        articles: list[dict[str, Any]] = []

        for item in items:
            article = self._parse_item(item)
            if not article:
                continue

            aid = self._article_id(article)

            # 跳过已推送过的
            if aid in seen_ids:
                continue

            # 关键词过滤（如果配了关键词）
            if self.keywords and not self._is_relevant(article):
                continue

            article["_id"] = aid
            articles.append(article)

            if len(articles) >= self.max_articles:
                break

        return articles

    async def collect_more(self, offset: int = 0) -> list[dict[str, Any]]:
        """继续抓取更多文章（跳过前 offset 条）."""
        seen_ids = self._load_seen_ids()

        proxy = _get_proxy_for_url(self.feed_url)
        client_kwargs: dict[str, Any] = dict(timeout=4, follow_redirects=True)
        if proxy:
            client_kwargs["proxy"] = proxy
        async with httpx.AsyncClient(**client_kwargs) as client:
            resp = await client.get(self.feed_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            })
            resp.raise_for_status()

        # XML 解析容错
        resp_text = resp.text.strip()
        if not resp_text or resp_text.startswith("<!DOCTYPE") or resp_text.startswith("<html"):
            raise ValueError(f"响应不是有效的 RSS/XML 格式")
        try:
            root = ElementTree.fromstring(resp_text)
        except ElementTree.ParseError as e:
            import re
            cleaned = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#)', '&amp;', resp_text)
            try:
                root = ElementTree.fromstring(cleaned)
            except ElementTree.ParseError:
                raise ValueError(f"RSS XML 解析失败: {e}")
        items = root.findall(".//item") or root.findall(
            ".//{http://www.w3.org/2005/Atom}entry"
        )

        articles: list[dict[str, Any]] = []
        skipped = 0

        for item in items:
            article = self._parse_item(item)
            if not article:
                continue

            aid = self._article_id(article)
            if aid in seen_ids:
                continue

            # 跳过已展示过的
            if skipped < offset:
                skipped += 1
                continue

            article["_id"] = aid
            articles.append(article)

            if len(articles) >= self.max_articles:
                break

        return articles

    def mark_as_seen(self, article_ids: list[str]) -> None:
        """将文章标记为已推送."""
        seen_ids = self._load_seen_ids()
        seen_ids.update(article_ids)
        self._save_seen_ids(seen_ids)

    def _parse_item(self, item: ElementTree.Element) -> dict[str, Any] | None:
        """解析单条 RSS item."""
        ns_atom = "{http://www.w3.org/2005/Atom}"

        # RSS 2.0 格式
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        description = item.findtext("description") or ""
        pub_date = item.findtext("pubDate") or ""

        # Atom 格式回退
        if not title:
            title = item.findtext(f"{ns_atom}title") or ""
        if not link:
            link_elem = item.find(f"{ns_atom}link")
            link = link_elem.get("href", "") if link_elem is not None else ""
        if not description:
            description = item.findtext(f"{ns_atom}summary") or ""
            if not description:
                description = item.findtext(f"{ns_atom}content") or ""
        if not pub_date:
            pub_date = item.findtext(f"{ns_atom}updated") or ""

        if not title:
            return None

        # 清理 HTML 标签（简单处理）
        import re
        clean_desc = re.sub(r"<[^>]+>", "", description).strip()
        # 截断描述
        if len(clean_desc) > 300:
            clean_desc = clean_desc[:300] + "..."

        return {
            "title": title.strip(),
            "url": link.strip(),
            "description": clean_desc,
            "pub_date": pub_date,
            "topic": self.topic,
            "source_name": self.name,
            "source_type": "rss",
            "tags": self.keywords[:5],  # 最多取 5 个关键词作为标签
        }

    def _is_relevant(self, article: dict[str, Any]) -> bool:
        """检查文章是否与关键词相关（无关键词则全部通过）."""
        if not self.keywords:
            return True

        text = f"{article.get('title', '')} {article.get('description', '')}".lower()
        return any(kw.lower() in text for kw in self.keywords)
