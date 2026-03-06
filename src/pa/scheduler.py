"""每日资讯调度器 - 聚合所有 RSS 源进行采集，支持分批抓取和交互式筛选."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pa.collectors.rss import RSSCollector
from pa.config import Config, load_config

# 每批抓取的 RSS 源数量（控制单次 MCP 调用耗时在 10 秒内）
BATCH_SIZE = 2
# 单个 RSS 源的抓取超时（秒），超时则跳过该源
PER_SOURCE_TIMEOUT = 5


class DailyDigestScheduler:
    """每日资讯调度器.

    职责：
    1. 读取配置中的 RSS 源
    2. 分批抓取文章（每批 BATCH_SIZE 个源，避免 MCP 超时）
    3. 将抓取结果缓存到本地文件，支持跨调用累积
    4. 提供交互式筛选（展示 → 用户选择 → 保存 → 可继续抓取）
    """

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or load_config()
        self._raw_dir = Path(self.config.sync.raw_dir).resolve()
        self._context_dir = Path(self.config.sync.context_dir).resolve()
        # 缓存当前批次的文章（用于交互式选择）
        self._current_batch: list[dict[str, Any]] = []
        self._collectors: list[RSSCollector] = []
        self._offset_map: dict[str, int] = {}  # 每个源的偏移量

    @property
    def _cache_file(self) -> Path:
        """分批抓取的缓存文件路径."""
        cache_dir = self._raw_dir / "rss"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / ".batch_cache.json"

    def _load_cache(self) -> dict[str, Any]:
        """加载分批抓取缓存."""
        if self._cache_file.exists():
            try:
                with open(self._cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
                # 检查缓存是否是今天的（跨天自动失效）
                cached_date = cache.get("date", "")
                today = datetime.now().strftime("%Y-%m-%d")
                if cached_date == today:
                    return cache
            except Exception:
                pass
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "next_batch_index": 0,
            "total_batches": 0,
            "articles": [],
            "errors": [],
            "sources_checked": 0,
            "completed": False,
        }

    def _save_cache(self, cache: dict[str, Any]) -> None:
        """保存分批抓取缓存."""
        self._cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

    def reset_cache(self) -> None:
        """重置缓存（开始新一轮采集时调用）."""
        if self._cache_file.exists():
            self._cache_file.unlink()

    @property
    def is_fetching_complete(self) -> bool:
        """检查是否所有批次都已抓取完成."""
        cache = self._load_cache()
        return cache.get("completed", False)

    def get_cached_articles(self) -> list[dict[str, Any]]:
        """获取缓存中已抓取的所有文章."""
        cache = self._load_cache()
        return cache.get("articles", [])

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

    async def _collect_one(self, collector: RSSCollector) -> tuple[list[dict[str, Any]], str | None]:
        """抓取单个 RSS 源，返回 (文章列表, 错误信息或None).

        自带 PER_SOURCE_TIMEOUT 秒超时保护，超时直接跳过。
        """
        try:
            articles = await asyncio.wait_for(
                collector.collect(),
                timeout=PER_SOURCE_TIMEOUT,
            )
            return articles, None
        except asyncio.TimeoutError:
            return [], f"[{collector.name}] 抓取超时（>{PER_SOURCE_TIMEOUT}s），已跳过"
        except Exception as e:
            return [], f"[{collector.name}] 抓取失败: {e}"

    async def fetch_articles(self) -> dict[str, Any]:
        """分批抓取 RSS 源的最新文章.

        每次调用只抓取一批（BATCH_SIZE 个源），结果缓存到本地文件。
        多次调用自动续抓下一批，直到所有源抓取完毕。

        Returns:
            {
                "articles": [...],           # 本批次新抓到的文章
                "all_articles": [...],       # 累积的所有文章
                "sources_checked": int,       # 本批次检查的源数
                "total_sources": int,         # 总源数
                "total_found": int,           # 累积找到的文章总数
                "errors": [...],              # 本批次的错误
                "all_errors": [...],          # 累积的所有错误
                "batch_index": int,           # 当前批次号（从 0 开始）
                "total_batches": int,         # 总批次数
                "completed": bool,            # 是否所有批次都已完成
            }
        """
        all_collectors = self._build_collectors()
        if not all_collectors:
            return {
                "articles": [],
                "all_articles": [],
                "sources_checked": 0,
                "total_sources": 0,
                "total_found": 0,
                "errors": ["未配置任何 RSS 源"],
                "all_errors": ["未配置任何 RSS 源"],
                "batch_index": 0,
                "total_batches": 0,
                "completed": True,
            }

        # 将所有 collector 分批
        total_batches = (len(all_collectors) + BATCH_SIZE - 1) // BATCH_SIZE

        # 加载缓存，确定当前要抓哪一批
        cache = self._load_cache()
        batch_index = cache.get("next_batch_index", 0)

        # 如果已经全部完成，直接返回缓存结果
        if cache.get("completed", False):
            cached_articles = cache.get("articles", [])
            self._current_batch = cached_articles
            self._collectors = all_collectors
            return {
                "articles": [],
                "all_articles": cached_articles,
                "sources_checked": 0,
                "total_sources": len(all_collectors),
                "total_found": len(cached_articles),
                "errors": [],
                "all_errors": cache.get("errors", []),
                "batch_index": batch_index,
                "total_batches": total_batches,
                "completed": True,
            }

        # 取出当前批次的 collectors
        start = batch_index * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(all_collectors))
        batch_collectors = all_collectors[start:end]

        # 并行抓取当前批次
        batch_articles: list[dict[str, Any]] = []
        batch_errors: list[str] = []

        tasks = [self._collect_one(c) for c in batch_collectors]
        results = await asyncio.gather(*tasks)

        for collector, (articles, error) in zip(batch_collectors, results):
            if error:
                batch_errors.append(error)
            else:
                batch_articles.extend(articles)
                self._offset_map[collector.name] = len(articles)

        # 更新缓存
        cached_articles = cache.get("articles", [])
        cached_errors = cache.get("errors", [])
        cached_articles.extend(batch_articles)
        cached_errors.extend(batch_errors)

        next_batch = batch_index + 1
        completed = next_batch >= total_batches

        cache.update({
            "next_batch_index": next_batch,
            "total_batches": total_batches,
            "articles": cached_articles,
            "errors": cached_errors,
            "sources_checked": cache.get("sources_checked", 0) + len(batch_collectors),
            "completed": completed,
        })
        self._save_cache(cache)

        # 同步到内存
        self._current_batch = cached_articles
        self._collectors = all_collectors

        return {
            "articles": batch_articles,
            "all_articles": cached_articles,
            "sources_checked": len(batch_collectors),
            "total_sources": len(all_collectors),
            "total_found": len(cached_articles),
            "errors": batch_errors,
            "all_errors": cached_errors,
            "batch_index": batch_index,
            "total_batches": total_batches,
            "completed": completed,
        }

    async def _collect_more_one(self, collector: RSSCollector, offset: int) -> tuple[list[dict[str, Any]], str | None]:
        """继续抓取单个 RSS 源的更多文章."""
        try:
            articles = await collector.collect_more(offset=offset)
            return articles, None
        except Exception as e:
            return [], f"[{collector.name}] 继续抓取失败: {e}"

    async def fetch_more(self) -> dict[str, Any]:
        """继续抓取更多文章（并行抓取，从上次的偏移位置继续）.

        Returns:
            同 fetch_articles 格式
        """
        if not self._collectors:
            self._collectors = self._build_collectors()

        new_articles: list[dict[str, Any]] = []
        errors: list[str] = []

        # 并行抓取所有 RSS 源
        tasks = [
            self._collect_more_one(c, self._offset_map.get(c.name, 0))
            for c in self._collectors
        ]
        results = await asyncio.gather(*tasks)

        for collector, (articles, error) in zip(self._collectors, results):
            if error:
                errors.append(error)
            else:
                offset = self._offset_map.get(collector.name, 0)
                new_articles.extend(articles)
                self._offset_map[collector.name] = offset + len(articles)

        self._current_batch.extend(new_articles)

        return {
            "articles": new_articles,
            "all_articles": self._current_batch,
            "sources_checked": len(self._collectors),
            "total_sources": len(self._collectors),
            "total_found": len(new_articles),
            "errors": errors,
            "all_errors": errors,
            "batch_index": 0,
            "total_batches": 1,
            "completed": True,
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
        # 确保内存中有数据（可能是从缓存恢复的）
        if not self._current_batch:
            self._current_batch = self.get_cached_articles()
        if not self._collectors:
            self._collectors = self._build_collectors()

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
