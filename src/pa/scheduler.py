"""每日资讯调度器 - 聚合所有 RSS 源进行采集，支持交互式筛选."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pa.collectors.rss import RSSCollector
from pa.config import Config, load_config


class DailyDigestScheduler:
    """每日资讯调度器.

    职责：
    1. 读取配置中的 RSS 源
    2. 聚合所有源的文章
    3. 提供交互式筛选（展示 → 用户选择 → 保存 → 可继续抓取）
    """

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or load_config()
        self._raw_dir = Path(self.config.sync.raw_dir).resolve()
        self._context_dir = Path(self.config.sync.context_dir).resolve()
        # 缓存当前批次的文章（用于交互式选择）
        self._current_batch: list[dict[str, Any]] = []
        self._collectors: list[RSSCollector] = []
        self._offset_map: dict[str, int] = {}  # 每个源的偏移量

    def _build_collectors(self) -> list[RSSCollector]:
        """根据配置构建所有 RSS 采集器."""
        collectors: list[RSSCollector] = []
        feeds_config = self.config.feeds

        if not feeds_config or not feeds_config.rss:
            return collectors

        rss_feeds = feeds_config.rss
        max_per_source = feeds_config.max_articles_per_source

        for feed in rss_feeds:
            collector = RSSCollector(
                name=feed["name"],
                raw_dir=self._raw_dir / "rss",
                feed_url=feed["url"],
                topic=feed.get("topic", "reading"),
                keywords=feed.get("keywords", []),
                max_articles=max_per_source,
            )
            collectors.append(collector)

        return collectors

    async def fetch_articles(self) -> dict[str, Any]:
        """首次抓取所有 RSS 源的最新文章.

        Returns:
            {
                "articles": [...],       # 文章列表
                "sources_checked": int,   # 检查的源数
                "total_found": int,       # 找到的文章数
                "errors": [...]           # 错误信息
            }
        """
        self._collectors = self._build_collectors()
        self._current_batch = []
        self._offset_map = {}
        errors: list[str] = []

        for collector in self._collectors:
            try:
                articles = await collector.collect()
                self._current_batch.extend(articles)
                self._offset_map[collector.name] = len(articles)
            except Exception as e:
                errors.append(f"[{collector.name}] 抓取失败: {e}")

        return {
            "articles": self._current_batch,
            "sources_checked": len(self._collectors),
            "total_found": len(self._current_batch),
            "errors": errors,
        }

    async def fetch_more(self) -> dict[str, Any]:
        """继续抓取更多文章（从上次的偏移位置继续）.

        Returns:
            同 fetch_articles 格式
        """
        if not self._collectors:
            self._collectors = self._build_collectors()

        new_articles: list[dict[str, Any]] = []
        errors: list[str] = []

        for collector in self._collectors:
            try:
                offset = self._offset_map.get(collector.name, 0)
                articles = await collector.collect_more(offset=offset)
                new_articles.extend(articles)
                self._offset_map[collector.name] = offset + len(articles)
            except Exception as e:
                errors.append(f"[{collector.name}] 继续抓取失败: {e}")

        self._current_batch.extend(new_articles)

        return {
            "articles": new_articles,
            "sources_checked": len(self._collectors),
            "total_found": len(new_articles),
            "errors": errors,
        }

    def save_selected(self, selected_indices: list[int]) -> dict[str, Any]:
        """保存用户选中的文章到知识库.

        Args:
            selected_indices: 用户选择的文章索引列表（从 1 开始）

        Returns:
            {
                "saved_count": int,
                "files_written": [...],
                "marked_seen": int,
            }
        """
        from pa.formatters.obsidian import ObsidianFormatter
        from pa.topics.manager import TopicManager

        formatter = ObsidianFormatter()
        topic_manager = TopicManager(self.config, self._raw_dir)
        files_written: list[str] = []
        saved_ids: list[str] = []
        all_ids: list[str] = []

        # 收集所有当前批次的 ID（无论是否选中都标记为已推送）
        for article in self._current_batch:
            if "_id" in article:
                all_ids.append(article["_id"])

        for idx in selected_indices:
            # 索引从 1 开始
            real_idx = idx - 1
            if real_idx < 0 or real_idx >= len(self._current_batch):
                continue

            article = self._current_batch[real_idx]
            topic = article.get("topic", "reading")

            # 确保主题存在
            if not topic_manager.topic_exists(topic):
                topic_name = topic.replace("-", " ").title()
                topic_manager.create_topic(
                    key=topic,
                    name=topic_name,
                    description=f"{topic_name}相关的收藏文章",
                    auto_created=True,
                )

            # 生成 Obsidian 格式内容
            now = datetime.now()
            title = article.get("title", "无标题")
            safe_title = "".join(
                c if c.isalnum() or c in "_-" else "_" for c in title
            )[:40]

            content = self._build_article_content(article, now)

            # 保存到 __collected/rss/{topic}/
            topic_dir = self._context_dir / "__collected" / "rss" / topic
            topic_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{safe_title}_{now.strftime('%Y%m%d')}.md"
            filepath = topic_dir / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            files_written.append(str(filepath))

            if "_id" in article:
                saved_ids.append(article["_id"])

            # 更新主题计数
            topic_manager.increment_content_count(topic)

        # 将所有推送过的文章（包括用户没选的）标记为已读，下次不再推送
        for collector in self._collectors:
            collector_ids = [
                a["_id"]
                for a in self._current_batch
                if a.get("source_name") == collector.name and "_id" in a
            ]
            if collector_ids:
                collector.mark_as_seen(collector_ids)

        return {
            "saved_count": len(files_written),
            "files_written": files_written,
            "marked_seen": len(all_ids),
        }

    def _build_article_content(self, article: dict[str, Any], now: datetime) -> str:
        """为单篇文章生成 Obsidian 格式的知识库内容."""
        title = article.get("title", "无标题")
        url = article.get("url", "")
        description = article.get("description", "")
        source_name = article.get("source_name", "RSS")
        topic = article.get("topic", "reading")
        pub_date = article.get("pub_date", "")
        tags = article.get("tags", [])

        tags_str = ", ".join([f'"{t}"' for t in tags]) if tags else f'"{topic}"'

        return f"""---
created: "{now.strftime('%Y-%m-%d %H:%M:%S')}"
modified: "{now.strftime('%Y-%m-%d %H:%M:%S')}"
tags: [{tags_str}, "collected", "rss"]
source-type: collected
source: rss
url: "{url}"
status: collected
---

# {title}

> **来源**: {source_name}
> **发布日期**: {pub_date or '未知'}
> **原文链接**: [{url}]({url})

---

{description}

---

*通过 RSS 自动采集于 {now.strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def skip_all(self) -> int:
        """跳过当前批次所有文章（全部标记为已推送但不保存）.

        Returns:
            标记的文章数
        """
        all_ids: list[str] = []
        for article in self._current_batch:
            if "_id" in article:
                all_ids.append(article["_id"])

        for collector in self._collectors:
            collector_ids = [
                a["_id"]
                for a in self._current_batch
                if a.get("source_name") == collector.name and "_id" in a
            ]
            if collector_ids:
                collector.mark_as_seen(collector_ids)

        return len(all_ids)
