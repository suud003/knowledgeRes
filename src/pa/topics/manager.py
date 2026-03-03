"""主题管理器 - 动态主题发现、创建和演进."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from pa.config.settings import Config, TopicConfig


@dataclass
class DynamicTopic:
    """动态主题数据结构."""

    name: str
    description: str
    keywords: list[str] = field(default_factory=list)
    parent: str | None = None  # 父主题 key
    created_at: str = ""
    updated_at: str = ""
    auto_created: bool = True
    content_count: int = 0
    related_topics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DynamicTopic":
        """从字典创建."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            keywords=data.get("keywords", []),
            parent=data.get("parent"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            auto_created=data.get("auto_created", True),
            content_count=data.get("content_count", 0),
            related_topics=data.get("related_topics", []),
        )

    def to_topic_config(self) -> TopicConfig:
        """转换为 TopicConfig 对象."""
        return TopicConfig(
            name=self.name,
            description=self.description,
            keywords=self.keywords,
        )


class TopicManager:
    """主题管理器 - 支持动态主题管理."""

    # 预定义的层级标签映射
    HIERARCHY_MAPPING = {
        # 顶层领域
        "ai": {"parent": None, "level": 1},
        "product": {"parent": None, "level": 1},
        "work": {"parent": None, "level": 1},
        "life": {"parent": None, "level": 1},
        "reading": {"parent": None, "level": 1},
        "entrepreneurship": {"parent": None, "level": 1},
        "health": {"parent": None, "level": 1},
        "parenting": {"parent": None, "level": 1},

        # AI 子主题
        "agent": {"parent": "ai", "level": 2},
        "model": {"parent": "ai", "level": 2},
        "prompt": {"parent": "ai", "level": 2},
        "mcp": {"parent": "ai/agent", "level": 3},
        "claude": {"parent": "ai/agent", "level": 3},

        # 产品子主题
        "growth": {"parent": "product", "level": 2},
        "ux": {"parent": "product", "level": 2},
        "strategy": {"parent": "product", "level": 2},

        # 工作子主题
        "management": {"parent": "work", "level": 2},
        "interview": {"parent": "work", "level": 2},

        # 生活子主题
        "装修": {"parent": "life", "level": 2},
        "育儿": {"parent": "parenting", "level": 2},
    }

    def __init__(self, config: Config, data_dir: Path | str = "data") -> None:
        """初始化主题管理器.

        Args:
            config: 应用配置
            data_dir: 数据目录路径
        """
        self.config = config
        self.data_dir = Path(data_dir)
        self.topics_file = self.data_dir / "topics.json"

        # 加载动态主题
        self.dynamic_topics: dict[str, DynamicTopic] = {}
        self._load_dynamic_topics()

    def _load_dynamic_topics(self) -> None:
        """从文件加载动态主题."""
        if self.topics_file.exists():
            try:
                with open(self.topics_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for key, topic_data in data.get("topics", {}).items():
                        self.dynamic_topics[key] = DynamicTopic.from_dict(topic_data)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"加载动态主题失败: {e}")
                self.dynamic_topics = {}

    def _save_dynamic_topics(self) -> None:
        """保存动态主题到文件."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "topics": {
                key: topic.to_dict()
                for key, topic in self.dynamic_topics.items()
            },
            "updated_at": datetime.now().isoformat(),
        }
        with open(self.topics_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_all_topics(self) -> dict[str, TopicConfig]:
        """获取所有主题（配置 + 动态）."""
        # 从配置获取静态主题
        all_topics = self.config.context.get_all_topics().copy()

        # 添加动态主题
        for key, dynamic_topic in self.dynamic_topics.items():
            if key not in all_topics:
                all_topics[key] = dynamic_topic.to_topic_config()

        return all_topics

    def topic_exists(self, topic_key: str) -> bool:
        """检查主题是否存在."""
        return (
            topic_key in self.config.context.get_all_topics()
            or topic_key in self.dynamic_topics
        )

    def create_topic(
        self,
        key: str,
        name: str,
        description: str = "",
        keywords: list[str] | None = None,
        parent: str | None = None,
        auto_created: bool = True,
    ) -> DynamicTopic:
        """创建新主题.

        Args:
            key: 主题唯一标识（小写，无空格）
            name: 主题显示名称
            description: 主题描述
            keywords: 关键词列表
            parent: 父主题 key（用于层级关系）
            auto_created: 是否自动创建

        Returns:
            创建的动态主题对象
        """
        now = datetime.now().isoformat()

        # 标准化 key
        key = self._normalize_key(key)

        # 如果主题已存在，返回现有主题
        if key in self.dynamic_topics:
            return self.dynamic_topics[key]

        # 推断层级关系
        if parent is None and key in self.HIERARCHY_MAPPING:
            parent = self.HIERARCHY_MAPPING[key].get("parent")

        # 创建主题
        topic = DynamicTopic(
            name=name,
            description=description or f"{name}相关的内容",
            keywords=keywords or [name],
            parent=parent,
            created_at=now,
            updated_at=now,
            auto_created=auto_created,
            content_count=0,
        )

        self.dynamic_topics[key] = topic
        self._save_dynamic_topics()

        return topic

    def auto_create_topic_from_content(
        self,
        content: str,
        title: str,
        suggested_key: str | None = None,
    ) -> tuple[str, DynamicTopic]:
        """基于内容自动创建主题.

        分析内容特征，自动推断主题信息.

        Args:
            content: 内容文本
            title: 标题
            suggested_key: 建议的主题 key

        Returns:
            (topic_key, topic_object)
        """
        # 如果提供了建议的 key，直接使用
        if suggested_key:
            key = self._normalize_key(suggested_key)
            if self.topic_exists(key):
                return key, self.dynamic_topics.get(
                    key,
                    DynamicTopic(
                        name=key,
                        description=f"{key} 相关内容",
                    ),
                )

        # 分析内容提取关键词
        keywords = self._extract_keywords(content, title)

        # 根据关键词推断主题
        inferred_topic = self._infer_topic_from_keywords(keywords)

        if inferred_topic and not self.topic_exists(inferred_topic):
            # 创建新主题
            name = self._key_to_name(inferred_topic)
            topic = self.create_topic(
                key=inferred_topic,
                name=name,
                description=f"{name}相关的文章、笔记和思考",
                keywords=keywords[:5],  # 取前5个关键词
                auto_created=True,
            )
            return inferred_topic, topic

        # 如果无法推断或主题已存在，返回默认主题
        return "reflection", self.dynamic_topics.get(
            "reflection",
            DynamicTopic(name="日记反思", description="日记和反思内容"),
        )

    def update_topic_keywords(self, topic_key: str, new_keywords: list[str]) -> bool:
        """更新主题关键词.

        用于主题的持续演进.
        """
        if topic_key in self.dynamic_topics:
            topic = self.dynamic_topics[topic_key]
            # 合并关键词，去重
            topic.keywords = list(set(topic.keywords + new_keywords))
            topic.updated_at = datetime.now().isoformat()
            self._save_dynamic_topics()
            return True
        return False

    def increment_content_count(self, topic_key: str) -> None:
        """增加主题的内容计数."""
        if topic_key in self.dynamic_topics:
            self.dynamic_topics[topic_key].content_count += 1
            self._save_dynamic_topics()

    def find_similar_topics(self, topic_key: str, threshold: float = 0.5) -> list[str]:
        """查找相似主题.

        基于关键词重叠度计算相似度.

        Args:
            topic_key: 要比较的主题
            threshold: 相似度阈值

        Returns:
            相似主题 key 列表
        """
        all_topics = self.get_all_topics()

        if topic_key not in all_topics:
            return []

        topic = all_topics[topic_key]
        topic_keywords = set(topic.keywords)

        similar = []
        for key, other_topic in all_topics.items():
            if key == topic_key:
                continue

            other_keywords = set(other_topic.keywords)
            if not other_keywords:
                continue

            # 计算 Jaccard 相似度
            intersection = topic_keywords & other_keywords
            union = topic_keywords | other_keywords
            similarity = len(intersection) / len(union) if union else 0

            if similarity >= threshold:
                similar.append(key)

        return similar

    def suggest_merge_topics(self) -> list[tuple[str, str, float]]:
        """建议合并的相似主题对.

        Returns:
            [(topic1, topic2, similarity), ...]
        """
        all_topics = self.get_all_topics()
        suggestions = []

        topic_keys = list(all_topics.keys())
        for i, key1 in enumerate(topic_keys):
            for key2 in topic_keys[i + 1:]:
                topic1 = all_topics[key1]
                topic2 = all_topics[key2]

                keywords1 = set(topic1.keywords)
                keywords2 = set(topic2.keywords)

                if not keywords1 or not keywords2:
                    continue

                intersection = keywords1 & keywords2
                union = keywords1 | keywords2
                similarity = len(intersection) / len(union) if union else 0

                if similarity >= 0.6:  # 高相似度阈值
                    suggestions.append((key1, key2, similarity))

        # 按相似度排序
        suggestions.sort(key=lambda x: x[2], reverse=True)
        return suggestions

    def get_topic_hierarchy(self, topic_key: str) -> list[str]:
        """获取主题的层级路径.

        例如: ai/agent/claude -> ["ai", "ai/agent", "ai/agent/claude"]
        """
        hierarchy = []
        current = topic_key

        while current:
            hierarchy.insert(0, current)
            if current in self.HIERARCHY_MAPPING:
                current = self.HIERARCHY_MAPPING[current].get("parent")
            elif current in self.dynamic_topics:
                current = self.dynamic_topics[current].parent
            else:
                break

        return hierarchy

    def _normalize_key(self, key: str) -> str:
        """标准化主题 key.

        - 转小写
        - 空格替换为连字符
        - 只保留字母、数字、连字符
        """
        return key.lower().strip().replace(" ", "-").replace("_", "-")

    def _key_to_name(self, key: str) -> str:
        """将 key 转换为显示名称."""
        return key.replace("-", " ").title()

    def _extract_keywords(self, content: str, title: str) -> list[str]:
        """从内容中提取关键词.

        简单的 TF-IDF 风格关键词提取.
        """
        # 合并标题和内容（标题权重更高）
        text = f"{title} {title} {content}"

        # 简单的分词（基于空格和标点）
        import re
        words = re.findall(r"\b[\u4e00-\u9fa5a-zA-Z]{2,}\b", text)

        # 统计词频
        from collections import Counter
        word_counts = Counter(words)

        # 过滤停用词（简化版）
        stopwords = {
            "一个", "这个", "那个", "什么", "怎么", "为什么",
            "the", "and", "for", "are", "but", "not", "you",
            "all", "can", "had", "her", "was", "one", "our",
        }

        # 返回高频词作为关键词
        keywords = [
            word for word, count in word_counts.most_common(20)
            if word.lower() not in stopwords and len(word) >= 2
        ]

        return keywords[:10]  # 返回前10个

    def _infer_topic_from_keywords(self, keywords: list[str]) -> str | None:
        """根据关键词推断主题.

        基于关键词匹配预定义的主题映射.
        """
        keyword_to_topic = {
            # AI 相关
            "ai": "ai",
            "agent": "ai/agent",
            "claude": "ai/agent/claude",
            "mcp": "ai/agent/mcp",
            "大模型": "ai/model",
            "llm": "ai/model",
            "prompt": "ai/prompt",

            # 产品相关
            "产品": "product",
            "产品经理": "product",
            "增长": "product/growth",
            "用户体验": "product/ux",

            # 工作相关
            "工作": "work",
            "团队": "work/management",
            "面试": "work/interview",

            # 阅读相关
            "阅读": "reading",
            "书籍": "reading",
            "笔记": "reading",
        }

        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in keyword_to_topic:
                return keyword_to_topic[keyword_lower]

        return None
