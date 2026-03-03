"""Context 路由引擎 - 支持 __created/__collected 目录分离和 Obsidian 格式."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from pa.config import Config, TopicConfig
from pa.formatters.obsidian import ObsidianFormatter
from pa.topics.manager import TopicManager


class RouterEngine:
    """Context 路由引擎 - 将原始数据路由到对应主题.

    支持功能：
    - 内容分离：原生内容(__created) vs 收集内容(__collected)
    - Obsidian 兼容格式：Frontmatter + 双链 + 层级标签
    - 来源细分：wechat/articles/flomo/feishu
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.topic_manager = TopicManager(config, config.sync.raw_dir)
        self.topics = self.topic_manager.get_all_topics()
        self.routing_config = config.routing
        self.formatter = ObsidianFormatter()

    def _calculate_match_score(self, record: dict[str, Any], topic: TopicConfig) -> float:
        """计算记录与主题的匹配分数."""
        if not topic.keywords:
            return 0.0

        # 构建待匹配的文本
        texts_to_match = []

        # 标题权重最高
        if title := record.get("title"):
            texts_to_match.append(str(title))
            texts_to_match.append(str(title))  # 标题算两次，增加权重

        # 内容
        if content := record.get("content"):
            texts_to_match.append(str(content))

        # 标签
        if tags := record.get("tags"):
            if isinstance(tags, list):
                texts_to_match.extend(str(t) for t in tags)
            else:
                texts_to_match.append(str(tags))

        full_text = " ".join(texts_to_match).lower()

        # 计算匹配的关键词数量
        matched_keywords = 0
        for keyword in topic.keywords:
            keyword_lower = keyword.lower()
            # 支持简单正则
            if keyword_lower.startswith("regex:"):
                pattern = keyword_lower[6:]
                if re.search(pattern, full_text):
                    matched_keywords += 1
            else:
                if keyword_lower in full_text:
                    matched_keywords += 1

        # 返回匹配比例
        return matched_keywords / len(topic.keywords)

    def route(self, record: dict[str, Any]) -> list[str]:
        """将单条记录路由到对应主题，返回主题 key 列表."""
        matches: list[tuple[str, float]] = []

        for topic_key, topic in self.topics.items():
            score = self._calculate_match_score(record, topic)
            if score >= self.routing_config.threshold:
                matches.append((topic_key, score))

        if not matches:
            # 检查记录是否有默认主题配置
            default_topic = record.get("default_topic")
            if default_topic and self.topic_manager.topic_exists(default_topic):
                return [default_topic]

            # 尝试自动创建主题
            if title := record.get("title"):
                content = record.get("content", "")
                topic_key, _ = self.topic_manager.auto_create_topic_from_content(
                    content=content,
                    title=title,
                    suggested_key=record.get("suggested_topic"),
                )
                return [topic_key]

            return []

        # 按匹配分数排序
        matches.sort(key=lambda x: x[1], reverse=True)

        if self.routing_config.allow_multi_topic:
            # 允许多主题：返回所有超过阈值的
            return [key for key, _ in matches]
        else:
            # 只返回最匹配的一个
            return [matches[0][0]]

    def route_batch(self, records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """批量路由记录，按主题分组."""
        # 获取所有可能的主题 key（包括动态主题）
        all_topic_keys = set(self.topics.keys())
        result: dict[str, list[dict[str, Any]]] = {key: [] for key in all_topic_keys}

        for record in records:
            topics = self.route(record)
            for topic_key in topics:
                if topic_key not in result:
                    result[topic_key] = []
                result[topic_key].append(record)

        return result

    def generate_context_file(self, topic_key: str, records: list[dict[str, Any]]) -> str:
        """为指定主题生成 Context Markdown 文件内容."""
        topic = self.topics.get(topic_key)
        if not topic:
            return ""

        lines: list[str] = []

        # 文件头（保留旧格式以保持向后兼容）
        lines.append(f"# {topic.name}")
        lines.append("")
        lines.append(f"> {topic.description}")
        lines.append("")
        lines.append(f"**记录数**: {len(records)}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # 按时间排序
        sorted_records = sorted(
            records,
            key=lambda x: x.get("created_time", ""),
            reverse=True,
        )

        # 生成每条记录的 Markdown
        for record in sorted_records:
            lines.extend(self._format_record(record))
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def generate_obsidian_file(
        self,
        topic_key: str,
        records: list[dict[str, Any]],
        content_type: str = "created",  # created | collected
    ) -> str:
        """生成 Obsidian 兼容格式的主题文件.

        Args:
            topic_key: 主题 key
            records: 记录列表
            content_type: 内容类型 (created/collected)

        Returns:
            Obsidian 兼容的 Markdown 内容
        """
        topic = self.topics.get(topic_key)
        if not topic:
            return ""

        lines: list[str] = []

        # 使用 Obsidian 格式化器生成文件头
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        frontmatter_lines = [
            "---",
            f'created: "{now}"',
            f'modified: "{now}"',
            f'tags: ["index", "{topic_key}", "{content_type}"]',
            f"source-type: {content_type}",
            "source: system",
            "status: processed",
            "---",
            "",
            f"# {topic.name}",
            "",
            f"> {topic.description}",
            "",
            f"**记录数**: {len(records)}",
            "",
            "## 目录",
            "",
        ]
        lines.extend(frontmatter_lines)

        # 按时间排序
        sorted_records = sorted(
            records,
            key=lambda x: x.get("created_time", ""),
            reverse=True,
        )

        # 生成目录
        for record in sorted_records:
            title = record.get("title", "无标题")
            date = str(record.get("created_time", ""))[:10]
            # 使用 Obsidian 双链格式
            safe_title = title.replace("[", "").replace("]", "")
            lines.append(f"- [[{safe_title}]] ({date})")

        lines.append("")
        lines.append("---")
        lines.append("")

        # 添加每条记录的 Obsidian 格式内容
        lines.append("## 内容")
        lines.append("")

        for record in sorted_records:
            formatted = self._format_obsidian_record(record, content_type)
            lines.append(formatted)
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _format_obsidian_record(self, record: dict[str, Any], content_type: str) -> str:
        """将单条记录格式化为 Obsidian 格式."""
        return self.formatter.format_note(
            title=record.get("title", "无标题"),
            content=record.get("content", ""),
            topic=record.get("topic", "reflection"),
            source_type=content_type,
            source=record.get("source", "mcp"),
            url=record.get("url", ""),
            author=record.get("author", ""),
            tags=record.get("tags", []),
            summary=record.get("summary", ""),
        )

    def _format_timestamp(self, ts: Any) -> str:
        """格式化时间戳为可读日期."""
        if not ts:
            return ""
        try:
            if isinstance(ts, (int, float)):
                # 飞书时间戳是毫秒
                if ts > 10000000000:
                    ts = ts / 1000
                return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
            return str(ts)
        except Exception:
            return str(ts)

    def _format_record(self, record: dict[str, Any]) -> list[str]:
        """将单条记录格式化为 Markdown（保留旧格式以保持兼容）."""
        lines: list[str] = []

        # 标题
        title = record.get("title", "无标题")
        lines.append(f"## {title}")
        lines.append("")

        # 元数据
        meta_parts = []
        if created := record.get("created_time"):
            formatted_date = self._format_timestamp(created)
            meta_parts.append(f"DATE: {formatted_date}")
        if source := record.get("source"):
            meta_parts.append(f"FROM: {source}")
        if tags := record.get("tags"):
            if isinstance(tags, list) and tags:
                meta_parts.append(f"TAGS: {' '.join(f'`{t}`' for t in tags)}")

        if meta_parts:
            lines.append(" | ".join(meta_parts))
            lines.append("")

        # 内容
        if content := record.get("content"):
            lines.append(content)
            lines.append("")

        # 附件处理
        if raw_fields := record.get("raw_fields"):
            attachments = self._extract_attachments(raw_fields)
            if attachments:
                lines.append("**附件**:")
                for name, url in attachments:
                    lines.append(f"- [{name}]({url})")
                lines.append("")

        return lines

    def _extract_attachments(self, fields: dict[str, Any]) -> list[tuple[str, str]]:
        """从字段中提取附件信息."""
        attachments: list[tuple[str, str]] = []

        # 处理 flomo 的图片格式 (images 列表)
        if "images" in fields and isinstance(fields["images"], list):
            for i, img_path in enumerate(fields["images"]):
                if isinstance(img_path, str):
                    attachments.append((f"图片_{i+1}", img_path))
            return attachments

        # 处理飞书附件格式
        for field_value in fields.values():
            if not isinstance(field_value, list):
                continue

            for item in field_value:
                if not isinstance(item, dict):
                    continue

                # 检查是否是附件类型
                if item.get("type") == "file":
                    name = item.get("name", "未命名文件")
                    url = item.get("tmp_download_url", "")
                    if url:
                        attachments.append((name, url))

        return attachments

    def write_context_files(
        self, routed_data: dict[str, list[dict[str, Any]]], output_dir: Path
    ) -> list[Path]:
        """将路由后的数据写入 Context 文件（旧方法，保持兼容）."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        written_files: list[Path] = []

        for topic_key, records in routed_data.items():
            if not records:
                continue

            content = self.generate_context_file(topic_key, records)
            if not content:
                continue

            # 按主题分目录
            topic_dir = output_dir / topic_key
            topic_dir.mkdir(exist_ok=True)

            # 文件名：topic_key_YYYYMMDD.md
            filename = f"{topic_key}_{datetime.now().strftime('%Y%m%d')}.md"
            filepath = topic_dir / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            written_files.append(filepath)

        return written_files

    def write_obsidian_files(
        self,
        routed_data: dict[str, list[dict[str, Any]]],
        output_dir: Path,
        content_type: str = "created",
    ) -> list[Path]:
        """将路由后的数据写入 Obsidian 格式的文件.

        Args:
            routed_data: 路由后的数据
            output_dir: 输出目录
            content_type: 内容类型 (created/collected)

        Returns:
            写入的文件路径列表
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        written_files: list[Path] = []

        for topic_key, records in routed_data.items():
            if not records:
                continue

            # 确定目录结构
            if content_type == "created":
                # 原生内容：__created/topic/
                target_dir = output_dir / "__created" / topic_key
            else:
                # 收集内容：__collected/topic/
                target_dir = output_dir / "__collected" / topic_key

            target_dir.mkdir(parents=True, exist_ok=True)

            # 生成 Obsidian 格式内容
            content = self.generate_obsidian_file(topic_key, records, content_type)
            if not content:
                continue

            # 文件名：topic_key_YYYYMMDD.md
            filename = f"{topic_key}_{datetime.now().strftime('%Y%m%d')}.md"
            filepath = target_dir / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            written_files.append(filepath)

            # 更新主题内容计数
            self.topic_manager.increment_content_count(topic_key)

        return written_files

    def write_collected_file(
        self,
        record: dict[str, Any],
        output_dir: Path,
        source_type: str = "articles",
    ) -> Path:
        """写入单条收集的内容到 __collected 目录.

        Args:
            record: 单条记录
            output_dir: Context 输出目录
            source_type: 来源类型 (wechat/articles/flomo)

        Returns:
            写入的文件路径
        """
        output_dir = Path(output_dir)

        # 确定目标目录：__collected/{source_type}/
        topic_key = record.get("topic", "uncategorized")
        target_dir = output_dir / "__collected" / source_type / topic_key
        target_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        title = record.get("title", "untitled")
        safe_title = re.sub(r"[^\w\s-]", "", title)[:30]
        filename = f"{safe_title}_{datetime.now().strftime('%Y%m%d')}.md"
        filepath = target_dir / filename

        # 生成 Obsidian 格式内容
        content = self.formatter.format_collection(
            title=title,
            content=record.get("content", ""),
            summary=record.get("summary", ""),
            tags=record.get("tags", []),
            topic=topic_key,
            url=record.get("url", ""),
            source_type=source_type,
            author=record.get("author", ""),
        )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        # 更新主题内容计数
        self.topic_manager.increment_content_count(topic_key)

        return filepath
