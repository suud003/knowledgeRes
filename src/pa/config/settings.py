"""配置管理模块."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class FeishuConfig:
    """飞书配置."""

    app_id: str = ""
    app_secret: str = ""
    bases: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class TopicConfig:
    """主题配置."""

    name: str = ""
    description: str = ""
    keywords: list[str] = field(default_factory=list)


@dataclass
class ContextConfig:
    """Context 配置."""

    core_topics: dict[str, TopicConfig] = field(default_factory=dict)
    custom_topics: dict[str, TopicConfig] = field(default_factory=dict)

    def get_all_topics(self) -> dict[str, TopicConfig]:
        """获取所有主题（核心+自定义）."""
        return {**self.core_topics, **self.custom_topics}


@dataclass
class RoutingConfig:
    """路由配置."""

    strategy: str = "keyword_match"  # keyword_match | ai_analysis
    threshold: float = 0.3
    allow_multi_topic: bool = True


@dataclass
class SyncConfig:
    """同步配置."""

    raw_dir: str = "data/raw"
    context_dir: str = "data/context"
    keep_history: bool = False


@dataclass
class ProxyConfig:
    """网络代理配置."""

    url: str = ""  # 代理地址，如 http://127.0.0.1:7890
    domains: list[str] = field(default_factory=list)  # 需要走代理的域名

    def get_proxy_for_url(self, url: str) -> str | None:
        """根据 URL 判断是否需要代理，返回代理地址或 None."""
        if not self.url:
            return None
        # 如果没配置 domains，所有请求都走代理
        if not self.domains:
            return self.url
        # 检查 URL 的域名是否在代理列表中
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        bare_domain = domain.removeprefix("www.")
        for d in self.domains:
            d_lower = d.lower().removeprefix("www.")
            if d_lower == bare_domain or d_lower == domain or d_lower in domain:
                return self.url
        return None


@dataclass
class FeedsConfig:
    """RSS 采集配置."""

    max_articles_per_source: int = 5
    rss: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Config:
    """主配置类."""

    feishu: FeishuConfig = field(default_factory=FeishuConfig)
    context: ContextConfig = field(default_factory=ContextConfig)
    routing: RoutingConfig = field(default_factory=RoutingConfig)
    sync: SyncConfig = field(default_factory=SyncConfig)
    feeds: FeedsConfig = field(default_factory=FeedsConfig)
    proxy: ProxyConfig = field(default_factory=ProxyConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Config:
        """从字典创建配置."""
        # 解析飞书配置
        feishu_data = data.get("feishu", {})
        feishu = FeishuConfig(
            app_id=feishu_data.get("app_id", ""),
            app_secret=feishu_data.get("app_secret", ""),
            bases=feishu_data.get("bases", []),
        )

        # 解析 Context 配置
        context_data = data.get("context", {})
        core_topics = {
            k: TopicConfig(
                name=v.get("name", ""),
                description=v.get("description", ""),
                keywords=v.get("keywords", []),
            )
            for k, v in context_data.get("core_topics", {}).items()
        }
        custom_topics = {
            k: TopicConfig(
                name=v.get("name", ""),
                description=v.get("description", ""),
                keywords=v.get("keywords", []),
            )
            for k, v in context_data.get("custom_topics", {}).items()
        }
        context = ContextConfig(core_topics=core_topics, custom_topics=custom_topics)

        # 解析路由配置
        routing_data = data.get("routing", {})
        routing = RoutingConfig(
            strategy=routing_data.get("strategy", "keyword_match"),
            threshold=routing_data.get("threshold", 0.3),
            allow_multi_topic=routing_data.get("allow_multi_topic", True),
        )

        # 解析同步配置
        sync_data = data.get("sync", {})
        sync = SyncConfig(
            raw_dir=sync_data.get("raw_dir", "data/raw"),
            context_dir=sync_data.get("context_dir", "data/context"),
            keep_history=sync_data.get("keep_history", False),
        )

        # 解析 Feeds 配置
        feeds_data = data.get("feeds", {})
        feeds = FeedsConfig(
            max_articles_per_source=feeds_data.get("max_articles_per_source", 5),
            rss=feeds_data.get("rss", []),
        )

        # 解析代理配置
        proxy_data = data.get("proxy", {})
        proxy = ProxyConfig(
            url=proxy_data.get("url", ""),
            domains=proxy_data.get("domains", []),
        )

        return cls(feishu=feishu, context=context, routing=routing, sync=sync, feeds=feeds, proxy=proxy)

    def validate(self) -> list[str]:
        """验证配置，返回错误列表."""
        errors = []

        if not self.feishu.app_id:
            errors.append("飞书 app_id 未配置")
        if not self.feishu.app_secret:
            errors.append("飞书 app_secret 未配置")
        if not self.feishu.bases:
            errors.append("飞书 bases 未配置")

        return errors


def find_config_file() -> Path | None:
    """查找配置文件."""
    # 按优先级查找
    candidates = [
        Path("config.yaml"),
        Path("config.local.yaml"),
        Path.home() / ".pa" / "config.yaml",
        Path(os.environ.get("PA_CONFIG", "")),
    ]

    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate

    return None


def load_config(config_path: Path | str | None = None) -> Config:
    """加载配置."""
    if config_path:
        config_file = Path(config_path)
    else:
        config_file = find_config_file()

    if not config_file or not config_file.exists():
        raise FileNotFoundError(
            "未找到配置文件。请复制 config.example.yaml 为 config.yaml 并填入配置。"
        )

    with open(config_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    config = Config.from_dict(data)
    
    # 将相对路径解析为绝对路径
    config_dir = config_file.parent
    config.sync.raw_dir = str((config_dir / config.sync.raw_dir).resolve())
    config.sync.context_dir = str((config_dir / config.sync.context_dir).resolve())
    
    return config
