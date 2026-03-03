"""Obsidian 兼容的 Markdown 格式化器.

支持功能:
- YAML Frontmatter 元数据
- 层级标签系统 (ai/agent/claude)
- WikiLinks 双链 ([[Concept]])
- 状态流转标记
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ObsidianFrontmatter:
    """Obsidian Frontmatter 数据结构."""

    created: str = ""
    modified: str = ""
    tags: list[str] = field(default_factory=list)
    source_type: str = ""  # created | collected
    source: str = ""  # wechat | articles | flomo | feishu | mcp
    url: str = ""
    author: str = ""
    status: str = "collected"  # collected | reading | processed | archived
    links: list[str] = field(default_factory=list)

    def to_yaml(self) -> str:
        """转换为 YAML 格式字符串."""
        lines = ["---"]

        if self.created:
            lines.append(f'created: "{self.created}"')
        if self.modified:
            lines.append(f'modified: "{self.modified}"')
        if self.tags:
            tags_str = ", ".join([f'"{tag}"' for tag in self.tags])
            lines.append(f"tags: [{tags_str}]")
        if self.source_type:
            lines.append(f"source-type: {self.source_type}")
        if self.source:
            lines.append(f"source: {self.source}")
        if self.url:
            lines.append(f'url: "{self.url}"')
        if self.author:
            lines.append(f'author: "{self.author}"')
        if self.status:
            lines.append(f"status: {self.status}")
        if self.links:
            links_str = ", ".join([f'"{link}"' for link in self.links])
            lines.append(f"links: [{links_str}]")

        lines.append("---")
        return "\n".join(lines)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ObsidianFrontmatter":
        """从字典创建."""
        return cls(
            created=data.get("created", ""),
            modified=data.get("modified", ""),
            tags=data.get("tags", []),
            source_type=data.get("source_type", ""),
            source=data.get("source", ""),
            url=data.get("url", ""),
            author=data.get("author", ""),
            status=data.get("status", "collected"),
            links=data.get("links", []),
        )


class ObsidianFormatter:
    """Obsidian 兼容的 Markdown 格式化器."""

    # 预定义的双链接识别模式
    WIKILINK_PATTERNS = {
        "people": ["Sam Altman", "张小龙", "雷军", "马斯克", "黄仁勋"],
        "companies": ["Anthropic", "OpenAI", "Notion", "Meta", "Google", "微软"],
        "ai_concepts": ["AI Agent", "LLM", "大模型", "MCP", "RAG", "Prompt"],
        "books": ["置身事内", "思考快与慢", "原则", "枪炮病菌与钢铁"],
    }

    def __init__(self) -> None:
        """初始化格式化器."""
        self.wikilink_patterns = self._build_wikilink_patterns()

    def _build_wikilink_patterns(self) -> list[tuple[str, str]]:
        """构建双链接识别模式列表."""
        patterns = []
        for category, items in self.WIKILINK_PATTERNS.items():
            for item in items:
                patterns.append((item.lower(), item))
        return patterns

    def format_note(
        self,
        title: str,
        content: str,
        topic: str,
        source_type: str = "created",
        source: str = "mcp",
        url: str = "",
        author: str = "",
        tags: list[str] | None = None,
        summary: str = "",
        **kwargs: Any,
    ) -> str:
        """格式化笔记为 Obsidian 兼容格式.

        Args:
            title: 笔记标题
            content: 笔记内容
            topic: 主题 key
            source_type: 内容类型 (created/collected)
            source: 来源标识
            url: 来源 URL
            author: 作者
            tags: 标签列表
            summary: 摘要
            **kwargs: 其他元数据

        Returns:
            Obsidian 兼容的 Markdown 字符串
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 构建层级标签
        hierarchical_tags = self._build_hierarchical_tags(topic, tags or [], source_type)

        # 提取双链接
        wikilinks = self._extract_wikilinks(content)

        # 构建 Frontmatter
        frontmatter = ObsidianFrontmatter(
            created=now,
            modified=now,
            tags=hierarchical_tags,
            source_type=source_type,
            source=source,
            url=url,
            author=author,
            status="collected" if source_type == "collected" else "created",
            links=wikilinks,
        )

        # 构建内容
        lines = [
            frontmatter.to_yaml(),
            "",
            f"# {title}",
            "",
        ]

        # 如果有摘要，添加摘要部分
        if summary:
            lines.extend([
                "## 摘要",
                "",
                summary,
                "",
            ])

        # 添加正文
        lines.extend([
            "## 正文",
            "",
            content,
            "",
        ])

        # 如果是收集的内容，添加来源信息
        if source_type == "collected" and url:
            lines.extend([
                "## 来源",
                "",
                f"- **原文**: [{title}]({url})",
            ])
            if author:
                lines.append(f"- **作者**: {author}")
            lines.append("")

        # 添加双链接引用
        if wikilinks:
            lines.extend([
                "## 相关链接",
                "",
            ])
            for link in wikilinks:
                lines.append(f"- {link}")
            lines.append("")

        # 添加分隔线
        lines.append("---")
        lines.append("")

        return "\n".join(lines)

    def format_collection(
        self,
        title: str,
        content: str,
        summary: str,
        tags: list[str],
        topic: str,
        url: str,
        source_type: str = "wechat",
        author: str = "",
    ) -> str:
        """格式化收集的文章.

        这是 collect_content 的专用格式化方法.
        """
        return self.format_note(
            title=title,
            content=content,
            topic=topic,
            source_type="collected",
            source=source_type,
            url=url,
            author=author,
            tags=tags,
            summary=summary,
        )

    def _build_hierarchical_tags(
        self,
        topic: str,
        tags: list[str],
        source_type: str,
    ) -> list[str]:
        """构建层级标签.

        格式: domain/subject/concept
        例如: ai/agent/claude, product/growth/viral
        """
        hierarchical_tags = []

        # 添加来源类型标签
        hierarchical_tags.append(source_type)

        # 添加主题作为标签
        topic_tag = self._normalize_tag(topic)
        if topic_tag:
            hierarchical_tags.append(topic_tag)

        # 处理传入的标签，转换为层级格式
        for tag in tags:
            # 如果标签已包含 "/"，说明已经是层级格式
            if "/" in tag:
                hierarchical_tags.append(tag)
            else:
                # 否则将标签附加到主题下
                # 例如: topic=ai, tag=agent -> ai/agent
                if topic_tag:
                    hierarchical_tags.append(f"{topic_tag}/{self._normalize_tag(tag)}")
                else:
                    hierarchical_tags.append(self._normalize_tag(tag))

        return list(set(hierarchical_tags))  # 去重

    def _normalize_tag(self, tag: str) -> str:
        """标准化标签格式.

        - 转小写
        - 空格替换为连字符
        - 移除特殊字符
        """
        # 转换为小写
        tag = tag.lower()
        # 替换空格和特殊字符为连字符
        tag = re.sub(r"[^\w\s-]", "", tag)
        tag = re.sub(r"[-\s]+", "-", tag)
        # 去除首尾连字符
        return tag.strip("-")

    def _extract_wikilinks(self, content: str) -> list[str]:
        """从内容中提取双链接.

        识别预定义的概念、人物、公司等.
        """
        wikilinks = []
        content_lower = content.lower()

        for pattern_lower, original in self.wikilink_patterns:
            # 检查是否包含该关键词
            if pattern_lower in content_lower:
                # 避免重复
                wikilink = f"[[{original}]]"
                if wikilink not in wikilinks:
                    wikilinks.append(wikilink)

        return wikilinks

    def add_wikilinks_to_content(self, content: str) -> str:
        """将内容中的关键词替换为双链接.

        例如: "AI Agent 是未来的趋势" -> "[[AI Agent]] 是未来的趋势"
        """
        for pattern_lower, original in self.wikilink_patterns:
            # 使用正则表达式替换，避免重复链接
            # 只在未加链接的情况下替换
            pattern = re.compile(
                rf"(?<!\[)(?<!\[\[)\b{re.escape(original)}\b(?!\]\])",
                re.IGNORECASE,
            )
            content = pattern.sub(f"[[{original}]]", content)

        return content

    def format_topic_index(
        self,
        topic_name: str,
        topic_description: str,
        records: list[dict[str, Any]],
    ) -> str:
        """格式化主题索引文件.

        用于生成主题的入口文件 (index.md).
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        frontmatter = ObsidianFrontmatter(
            created=now,
            modified=now,
            tags=["index", "meta"],
            source_type="meta",
            source="system",
            status="processed",
        )

        lines = [
            frontmatter.to_yaml(),
            "",
            f"# {topic_name}",
            "",
            f"> {topic_description}",
            "",
            f"**记录数**: {len(records)}",
            "",
            "## 目录",
            "",
        ]

        # 按日期排序的记录列表
        sorted_records = sorted(
            records,
            key=lambda r: r.get("created_time", ""),
            reverse=True,
        )

        for record in sorted_records:
            title = record.get("title", "无标题")
            date = record.get("created_time", "")[:10]  # 只取日期部分
            lines.append(f"- [[{title}]] ({date})")

        lines.append("")
        lines.append("---")
        lines.append("")

        return "\n".join(lines)

    def extract_links_for_graph(self, content: str) -> dict[str, list[str]]:
        """提取内容中的链接关系，用于图谱可视化.

        Returns:
            {
                "wikilinks": ["[[Concept1]]", "[[Concept2]]"],
                "external": ["https://example.com"],
                "tags": ["#tag1", "#tag2"],
            }
        """
        links = {
            "wikilinks": [],
            "external": [],
            "tags": [],
        }

        # 提取 WikiLinks
        wikilink_pattern = re.compile(r"\[\[(.*?)\]\]")
        links["wikilinks"] = wikilink_pattern.findall(content)

        # 提取外部链接
        external_pattern = re.compile(r"\[.*?\]\((https?://.*?)\)")
        links["external"] = external_pattern.findall(content)

        # 提取标签
        tag_pattern = re.compile(r"#(\w+)")
        links["tags"] = tag_pattern.findall(content)

        return links
