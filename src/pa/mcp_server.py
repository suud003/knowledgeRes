"""MCP Server - 为 Claude Code 提供个人助手工具.

支持功能:
- 数据同步 (sync_data)
- 内容收集 (collect_content) - 支持 Obsidian 格式和 __collected 目录
- 笔记添加 (add_note) - 支持 Obsidian 格式和 __created 目录
- 主题管理 (manage_topic) - 动态主题创建和管理
- Ship-Learn-Next 学习计划
"""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from pa.config import Config, load_config
from pa.config.settings import TopicConfig
from pa.formatters.obsidian import ObsidianFormatter
from pa.router.engine import RouterEngine
from pa.topics.manager import TopicManager

# 添加 ship-learn-next 到路径
SKILL_DIR = Path(__file__).parent.parent.parent / "skills" / "ship-learn-next" / "scripts"
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

# 创建 MCP Server
mcp = FastMCP("personal-assistant")

# 全局配置缓存
_config: Config | None = None
_topic_manager: TopicManager | None = None


def get_config() -> Config:
    """获取配置（带缓存）."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def get_topic_manager() -> TopicManager:
    """获取主题管理器（带缓存）."""
    global _topic_manager
    if _topic_manager is None:
        config = get_config()
        _topic_manager = TopicManager(config, config.sync.raw_dir)
    return _topic_manager


@mcp.tool()
async def sync_data() -> str:
    """触发数据同步和路由，将所有数据源的数据同步到 Context 文件夹.

    Returns:
        同步结果摘要，包含处理的数据条数和写入的文件列表
    """
    try:
        config = get_config()
        from pa.collectors.feishu import FeishuCollector

        raw_dir = Path(config.sync.raw_dir)
        context_dir = Path(config.sync.context_dir)

        all_records: list[dict[str, Any]] = []

        # 同步每个飞书数据源
        for base_config in config.feishu.bases:
            collector = FeishuCollector(
                name=base_config["name"],
                raw_dir=raw_dir / "feishu",
                app_id=config.feishu.app_id,
                app_secret=config.feishu.app_secret,
                app_token=base_config["app_token"],
                table_id=base_config["table_id"],
                field_mapping=base_config.get("fields"),
            )
            records = await collector.collect()
            # 标记为原生内容
            for record in records:
                record["content_type"] = "created"
                record["source"] = "feishu"
            all_records.extend(records)

        if not all_records:
            return "未获取到任何数据。请检查数据源配置。"

        # 路由数据到不同主题
        router = RouterEngine(config)
        routed = router.route_batch(all_records)

        # 写入 Context 文件（使用新的 Obsidian 格式和目录结构）
        written_files = router.write_obsidian_files(
            routed,
            context_dir,
            content_type="created",
        )

        # 生成摘要
        summary_lines = ["## 同步完成 ✓", ""]
        summary_lines.append(f"**总记录数**: {len(all_records)}")
        summary_lines.append("")
        summary_lines.append("**按主题分布**:")
        for topic_key, records in routed.items():
            if records:
                topic = router.topics.get(topic_key)
                topic_name = topic.name if topic else topic_key
                summary_lines.append(f"- {topic_name}: {len(records)} 条")
        summary_lines.append("")
        summary_lines.append(f"**写入文件数**: {len(written_files)}")
        summary_lines.append("")
        summary_lines.append("**存储位置**: `data/context/__created/`")
        summary_lines.append("")
        summary_lines.append("**文件列表**:")
        for f in written_files[:10]:  # 最多显示10个
            summary_lines.append(f"- {f.name}")
        if len(written_files) > 10:
            summary_lines.append(f"- ... 等共 {len(written_files)} 个文件")

        return "\n".join(summary_lines)

    except Exception as e:
        return f"同步失败: {type(e).__name__}: {e}"


@mcp.tool()
async def list_topics() -> str:
    """列出所有可用的 Context 主题及其描述.

    Returns:
        主题列表的 Markdown 格式文本
    """
    try:
        config = get_config()
        topic_manager = get_topic_manager()
        topics = topic_manager.get_all_topics()

        if not topics:
            return "未配置任何主题。"

        lines = ["## 可用主题", ""]

        # 核心主题
        if config.context.core_topics:
            lines.append("### 核心主题")
            lines.append("")
            for key, topic in config.context.core_topics.items():
                lines.append(f"**{topic.name}** (`{key}`)")
                lines.append(f"> {topic.description}")
                if topic.keywords:
                    lines.append(f"关键词: {', '.join(topic.keywords[:5])}...")
                lines.append("")

        # 自定义主题
        if config.context.custom_topics:
            lines.append("### 自定义主题")
            lines.append("")
            for key, topic in config.context.custom_topics.items():
                lines.append(f"**{topic.name}** (`{key}`)")
                lines.append(f"> {topic.description}")
                lines.append("")

        # 动态主题
        if topic_manager.dynamic_topics:
            lines.append("### 动态主题 (AI 自动创建)")
            lines.append("")
            for key, topic in topic_manager.dynamic_topics.items():
                if key not in config.context.get_all_topics():
                    lines.append(f"**{topic.name}** (`{key}`)")
                    lines.append(f"> {topic.description}")
                    lines.append(f"内容数: {topic.content_count}")
                    lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return f"获取主题列表失败: {type(e).__name__}: {e}"


@mcp.tool()
async def get_context(topic: str | None = None) -> str:
    """获取指定主题的 Context 内容，用于回答相关问题.

    Args:
        topic: 主题 key（如 'personal', 'writing', 'tasks'），不传则返回所有主题

    Returns:
        Context 内容的 Markdown 文本
    """
    try:
        config = get_config()
        context_dir = Path(config.sync.context_dir)

        if not context_dir.exists():
            return "Context 目录不存在。请先运行 sync_data 进行同步。"

        # 如果指定了主题，只读取该主题
        if topic:
            # 尝试在新旧两个位置查找
            search_paths = [
                context_dir / "__created" / topic,
                context_dir / "__collected" / topic,
                context_dir / topic,  # 旧位置
            ]

            for topic_dir in search_paths:
                if topic_dir.exists():
                    files = sorted(topic_dir.glob("*.md"), reverse=True)
                    if files:
                        with open(files[0], "r", encoding="utf-8") as f:
                            return f.read()

            return f"主题 '{topic}' 暂无内容。"

        # 未指定主题，返回所有主题的摘要
        lines = ["## Context 总览", ""]

        # 优先读取 __created 目录
        created_dir = context_dir / "__created"
        if created_dir.exists():
            lines.append("### 原生内容 (__created)")
            lines.append("")
            for topic_dir in created_dir.iterdir():
                if topic_dir.is_dir():
                    files = list(topic_dir.glob("*.md"))
                    if files:
                        latest = max(files, key=lambda f: f.stat().st_mtime)
                        with open(latest, "r", encoding="utf-8") as f:
                            content = f.read()
                            preview = "\n".join(content.split("\n")[:5])
                            lines.append(f"**{topic_dir.name}** ({len(files)} 个文件)")
                            lines.append(preview[:200] + "...")
                            lines.append("")

        # 收集内容
        collected_dir = context_dir / "__collected"
        if collected_dir.exists():
            lines.append("### 收集内容 (__collected)")
            lines.append("")
            total_files = 0
            for source_dir in collected_dir.iterdir():
                if source_dir.is_dir():
                    count = len(list(source_dir.rglob("*.md")))
                    total_files += count
                    lines.append(f"- {source_dir.name}: {count} 个文件")
            lines.append(f"**总计**: {total_files} 个文件")
            lines.append("")

        if len(lines) <= 3:
            return "暂无 Context 内容。请先运行 sync_data 或 collect_content。"

        return "\n".join(lines)

    except Exception as e:
        return f"获取 Context 失败: {type(e).__name__}: {e}"


@mcp.tool()
async def query_context(query: str, topics: list[str] | None = None) -> str:
    """跨主题搜索相关内容，返回匹配的记录.

    Args:
        query: 搜索关键词
        topics: 限定搜索的主题列表，不传则搜索所有主题

    Returns:
        匹配的记录列表
    """
    try:
        config = get_config()
        context_dir = Path(config.sync.context_dir)

        if not context_dir.exists():
            return "Context 目录不存在。请先运行 sync_data 进行同步。"

        # 确定要搜索的目录
        search_dirs = []
        if topics:
            for topic in topics:
                search_dirs.extend([
                    context_dir / "__created" / topic,
                    context_dir / "__collected" / topic,
                    context_dir / topic,
                ])
        else:
            # 搜索所有目录
            search_dirs = [
                context_dir / "__created",
                context_dir / "__collected",
                context_dir,
            ]

        matches: list[tuple[str, str, float]] = []  # (topic, line, score)
        query_lower = query.lower()

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            # 递归搜索所有 markdown 文件
            for file in search_dir.rglob("*.md"):
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        content = f.read()

                    if query_lower in content.lower():
                        # 提取匹配的段落
                        paragraphs = content.split("\n## ")
                        for para in paragraphs:
                            if query_lower in para.lower():
                                score = para.lower().count(query_lower)
                                topic = file.parent.name
                                matches.append((topic, "## " + para if not para.startswith("## ") else para, score))
                except Exception:
                    continue

        if not matches:
            return f'未找到与 "{query}" 相关的内容。'

        # 按匹配分数排序
        matches.sort(key=lambda x: x[2], reverse=True)

        # 返回前 10 条
        lines = [f"## 搜索: '{query}'", f"**找到 {len(matches)} 条匹配**", ""]

        for topic, content, _ in matches[:10]:
            lines.append(f"### 来自: {topic}")
            lines.append(content[:500] + "..." if len(content) > 500 else content)
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return f"搜索失败: {type(e).__name__}: {e}"


@mcp.tool()
async def search_recent(days: int = 7, topic: str | None = None) -> str:
    """搜索最近 N 天的内容，返回按时间排序的记录.

    Args:
        days: 搜索最近多少天的内容，默认 7 天
        topic: 限定搜索的主题，不传则搜索所有主题

    Returns:
        匹配的记录列表，按时间倒序排列
    """
    try:
        config = get_config()
        context_dir = Path(config.sync.context_dir)

        if not context_dir.exists():
            return "Context 目录不存在。请先运行 sync_data 进行同步。"

        # 计算时间阈值
        cutoff_date = datetime.now() - timedelta(days=days)

        # 确定要搜索的目录
        search_dirs = []
        if topic:
            search_dirs = [
                context_dir / "__created" / topic,
                context_dir / "__collected" / topic,
                context_dir / topic,
            ]
        else:
            search_dirs = [context_dir / "__created", context_dir / "__collected", context_dir]

        matches: list[tuple[str, str, datetime]] = []  # (topic, content, date)

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for file in search_dir.rglob("*.md"):
                try:
                    # 检查文件修改时间
                    mtime = datetime.fromtimestamp(file.stat().st_mtime)
                    if mtime < cutoff_date:
                        continue

                    with open(file, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 提取日期信息（优先从 frontmatter 解析）
                    file_date = mtime
                    for line in content.split("\n")[:30]:  # 检查前30行
                        if line.startswith("created:"):
                            try:
                                date_str = line.split(":", 1)[1].strip().strip('"')
                                file_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                                break
                            except (ValueError, IndexError):
                                pass

                    if file_date >= cutoff_date:
                        topic_name = file.parent.name
                        matches.append((topic_name, content, file_date))
                except Exception:
                    continue

        if not matches:
            return f"最近 {days} 天内没有新内容。"

        # 按日期倒序排序
        matches.sort(key=lambda x: x[2], reverse=True)

        # 生成结果
        lines = [f"## 最近 {days} 天的内容", f"**找到 {len(matches)} 条记录**", ""]

        for topic_key, content, date in matches[:20]:  # 最多返回 20 条
            lines.append(f"### {topic_key} ({date.strftime('%Y-%m-%d')})")
            # 只显示前 800 字符
            preview = content[:800] + "..." if len(content) > 800 else content
            lines.append(preview)
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return f"搜索失败: {type(e).__name__}: {e}"


@mcp.tool()
async def add_note(content: str, topic: str, title: str | None = None) -> str:
    """快速添加笔记到指定主题.

    Args:
        content: 笔记内容
        topic: 主题 key（如 'reflection', 'writing', 'tasks'）
        title: 笔记标题，不传则使用时间戳

    Returns:
        添加结果
    """
    try:
        config = get_config()
        context_dir = Path(config.sync.context_dir)
        topic_manager = get_topic_manager()

        # 验证主题是否存在，不存在则自动创建
        if not topic_manager.topic_exists(topic):
            # 自动创建主题
            topic_name = topic.replace("-", " ").title()
            topic_manager.create_topic(
                key=topic,
                name=topic_name,
                description=f"{topic_name}相关的笔记和想法",
                auto_created=True,
            )

        # 使用 Obsidian 格式化器
        formatter = ObsidianFormatter()
        now = datetime.now()
        note_title = title or f"笔记 {now.strftime('%H:%M')}"

        # 生成 Obsidian 格式内容
        formatted_content = formatter.format_note(
            title=note_title,
            content=content,
            topic=topic,
            source_type="created",
            source="mcp",
        )

        # 写入 __created 目录
        target_dir = context_dir / "__created" / topic
        target_dir.mkdir(parents=True, exist_ok=True)

        safe_title = "".join(c if c.isalnum() or c in "_-" else "_" for c in note_title)
        filename = f"{topic}_{now.strftime('%Y%m%d')}_{safe_title[:20]}.md"
        filepath = target_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(formatted_content)

        # 更新主题内容计数
        topic_manager.increment_content_count(topic)

        return f"✅ 笔记已添加到 '__created/{topic}'\n文件: {filepath}\n格式: Obsidian 兼容"

    except Exception as e:
        return f"添加失败: {type(e).__name__}: {e}"


@mcp.tool()
async def collect_content(
    url: str,
    html: str,
    topic: str | None = None,
    download_images: bool = True,
) -> str:
    """收集网页内容到知识库（完整内容提取）.

    只需提供 URL 和 HTML，自动完成：
    - 完整正文提取（保留原始内容，不做摘要）
    - 元数据解析（标题、作者、发布时间）
    - 图片本地化（可选）
    - 保存到知识库

    Args:
        url: 网页 URL
        html: 网页 HTML 内容（使用 Playwright 抓取）
        topic: 目标主题（可选，不传则自动推断为 'reading'）
        download_images: 是否下载图片到本地（默认 True）

    Returns:
        处理结果摘要
    """
    try:
        from pa.extractors import WebExtractor, ImageHandler
        from pa.extractors.sites import WechatExtractor, ZhihuExtractor
        from urllib.parse import urlparse

        config = get_config()
        raw_dir = Path(config.sync.raw_dir)
        context_dir = Path(config.sync.context_dir)
        topic_manager = get_topic_manager()

        # 1. 选择合适的提取器
        domain = urlparse(url).netloc.lower()
        
        if "mp.weixin.qq.com" in domain or "weixin.qq.com" in domain:
            extractor = WechatExtractor()
        elif "zhihu.com" in domain:
            extractor = ZhihuExtractor()
        else:
            extractor = WebExtractor()
        
        # 2. 提取完整内容
        extracted = await extractor.extract(url, html)
        
        # 3. 处理图片（如果启用）
        image_infos = []
        processed_content = extracted.content
        
        if download_images and extracted.images:
            assets_dir = context_dir / "__collected" / "assets" / "images"
            image_handler = ImageHandler(assets_dir=assets_dir)
            processed_content, image_infos = await image_handler.process_content(
                extracted.content, source_url=url
            )
        
        # 4. 确定主题
        final_topic = topic or "reading"
        
        if not topic_manager.topic_exists(final_topic):
            topic_name = final_topic.replace("-", " ").title()
            topic_manager.create_topic(
                key=final_topic,
                name=topic_name,
                description=f"{topic_name}相关的收藏文章",
                auto_created=True,
            )
        
        # 5. 生成 Obsidian 格式内容（完整正文）
        now = datetime.now()
        safe_title = "".join(c if c.isalnum() or c in "_-" else "_" for c in extracted.title)[:50]
        
        # 生成知识库内容（Obsidian 格式，包含完整正文）
        obsidian_content = f"""---
created: "{now.strftime('%Y-%m-%d %H:%M:%S')}"
modified: "{now.strftime('%Y-%m-%d %H:%M:%S')}"
tags: ["{final_topic}", "collected", "{extracted.site_type}"]
source-type: collected
source: {extracted.site_type}
url: "{url}"
author: "{extracted.author or ''}"
publish_date: "{extracted.publish_date or ''}"
status: collected
---

# {extracted.title}

> **来源**: {extracted.site_name or extracted.site_type}
> **作者**: {extracted.author or '未知'}
> **发布日期**: {extracted.publish_date or '未知'}
> **原文链接**: [{url}]({url})

---

{processed_content}

---

*收集于 {now.strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # 6. 保存原始内容到 raw/collect/
        collect_dir = raw_dir / "collect"
        collect_dir.mkdir(parents=True, exist_ok=True)
        raw_filename = f"{extracted.site_type}_{now.strftime('%Y%m%d_%H%M%S')}_{safe_title}.md"
        raw_filepath = collect_dir / raw_filename
        
        with open(raw_filepath, "w", encoding="utf-8") as f:
            f.write(f"# {extracted.title}\n\n**URL**: {url}\n\n{processed_content}")
        
        # 7. 保存到知识库
        topic_dir = context_dir / "__collected" / extracted.site_type / final_topic
        topic_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{safe_title[:30]}_{now.strftime('%Y%m%d')}.md"
        filepath = topic_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(obsidian_content)
        
        # 8. 更新计数
        topic_manager.increment_content_count(final_topic)
        
        # 返回结果
        image_msg = f"\n🖼️ 图片: 已下载 {len(image_infos)} 张到本地" if image_infos else ""
        
        return f"""✅ 内容收集完成

📄 标题: {extracted.title}
👤 作者: {extracted.author or '未知'}
🏠 来源: {extracted.site_name or extracted.site_type}
📅 发布: {extracted.publish_date or '未知'}
📊 字数: {extracted.word_count}
🏷️ 类型: {extracted.site_type}
📍 主题: {final_topic}{image_msg}

💾 存储位置:
   - 原始数据: {raw_filepath}
   - 知识库: {filepath}

🔧 提取器: {extractor.name}
"""

    except ImportError as e:
        return f"""⚠️ 内容提取功能需要额外依赖

缺少: {e}

请安装依赖:
pip install trafilatura beautifulsoup4
"""
    except Exception as e:
        return f"❌ 收集失败: {type(e).__name__}: {e}"


@mcp.tool()
async def manage_topic(
    action: str,
    topic_key: str | None = None,
    name: str | None = None,
    description: str | None = None,
    keywords: list[str] | None = None,
    parent: str | None = None,
) -> str:
    """管理主题 - 创建、更新、删除或查询主题.

    Args:
        action: 操作类型 (create | update | delete | list | suggest_merge)
        topic_key: 主题 key（create/update/delete 时需要）
        name: 主题显示名称（create/update 时使用）
        description: 主题描述（create/update 时使用）
        keywords: 关键词列表（create/update 时使用）
        parent: 父主题 key（create 时使用，用于层级关系）

    Returns:
        操作结果

    Examples:
        # 创建新主题
        manage_topic(action="create", topic_key="agent-design", name="Agent 设计")

        # 列出所有主题
        manage_topic(action="list")

        # 建议合并的相似主题
        manage_topic(action="suggest_merge")
    """
    try:
        topic_manager = get_topic_manager()

        if action == "list":
            topics = topic_manager.get_all_topics()
            lines = [f"## 主题列表 ({len(topics)} 个)", ""]
            lines.append("| Key | 名称 | 关键词数量 | 类型 |")
            lines.append("|-----|------|-----------|------|")

            config = get_config()
            for key, topic in topics.items():
                topic_type = "核心" if key in config.context.core_topics else "动态"
                lines.append(f"| {key} | {topic.name} | {len(topic.keywords)} | {topic_type} |")

            return "\n".join(lines)

        elif action == "create":
            if not topic_key or not name:
                return "❌ 创建主题需要提供 topic_key 和 name"

            if topic_manager.topic_exists(topic_key):
                return f"❌ 主题 '{topic_key}' 已存在"

            topic = topic_manager.create_topic(
                key=topic_key,
                name=name,
                description=description or f"{name}相关的内容",
                keywords=keywords or [name],
                parent=parent,
                auto_created=False,
            )

            return f"""✅ 主题已创建

Key: {topic_key}
名称: {name}
描述: {topic.description}
关键词: {', '.join(topic.keywords[:5])}
父主题: {parent or '无'}
"""

        elif action == "update":
            if not topic_key:
                return "❌ 更新主题需要提供 topic_key"

            if topic_key not in topic_manager.dynamic_topics:
                return f"❌ 只能更新动态创建的主题（{topic_key} 是核心主题）"

            topic = topic_manager.dynamic_topics[topic_key]
            if name:
                topic.name = name
            if description:
                topic.description = description
            if keywords:
                topic.keywords = keywords
            if parent:
                topic.parent = parent

            topic.updated_at = datetime.now().isoformat()
            topic_manager._save_dynamic_topics()

            return f"✅ 主题 '{topic_key}' 已更新"

        elif action == "delete":
            if not topic_key:
                return "❌ 删除主题需要提供 topic_key"

            if topic_key not in topic_manager.dynamic_topics:
                return f"❌ 只能删除动态创建的主题"

            del topic_manager.dynamic_topics[topic_key]
            topic_manager._save_dynamic_topics()

            return f"✅ 主题 '{topic_key}' 已删除"

        elif action == "suggest_merge":
            suggestions = topic_manager.suggest_merge_topics()

            if not suggestions:
                return "未找到相似度高的主题对，无需合并。"

            lines = ["## 建议合并的主题对", ""]
            lines.append("| 主题1 | 主题2 | 相似度 |")
            lines.append("|-------|-------|--------|")

            for t1, t2, sim in suggestions[:10]:
                lines.append(f"| {t1} | {t2} | {sim:.2%} |")

            lines.append("")
            lines.append("💡 提示: 使用 `manage_topic(action='delete')` 删除重复主题")

            return "\n".join(lines)

        else:
            return f"❌ 未知操作: {action}。支持的操作: create, update, delete, list, suggest_merge"

    except Exception as e:
        return f"操作失败: {type(e).__name__}: {e}"


# ========== Ship-Learn-Next 工具 ==========

@mcp.tool()
async def create_ship_plan(
    topic: str,
    focus: str | None = None,
    duration_weeks: int = 4,
) -> str:
    """基于知识库内容创建 Ship-Learn-Next 实践计划.

    将知识转化为实践的迭代学习计划，遵循 SHIP(交付) → LEARN(反思) → NEXT(迭代) 循环。

    Args:
        topic: 知识来源主题 key（如 'reading', 'ai', 'product'）
        focus: 关注的具体知识点或方向（可选）
        duration_weeks: 计划周期周数（默认4周）

    Returns:
        创建结果摘要，包含计划文件路径

    Example:
        create_ship_plan(topic="reading", focus="Prompt Engineering", duration_weeks=4)
    """
    try:
        config = get_config()
        context_dir = Path(config.sync.context_dir)
        topic_manager = get_topic_manager()

        # 验证主题
        if not topic_manager.topic_exists(topic):
            available = ", ".join(topic_manager.get_all_topics().keys())
            return f"主题 '{topic}' 不存在。可用主题: {available}"

        # 读取知识内容（优先从新目录读取）
        topic_dirs = [
            context_dir / "__created" / topic,
            context_dir / "__collected" / topic,
            context_dir / topic,
        ]

        knowledge_content = ""
        for topic_dir in topic_dirs:
            if topic_dir.exists():
                files = sorted(topic_dir.glob("*.md"), reverse=True)
                if files:
                    with open(files[0], "r", encoding="utf-8") as f:
                        knowledge_content = f.read()
                        break

        if not knowledge_content:
            return f"主题 '{topic}' 暂无内容。请先运行 sync_data 或 collect_content。"

        # 如果指定了 focus，尝试提取相关内容
        if focus:
            lines = knowledge_content.split("\n")
            relevant_lines = []
            for line in lines:
                if focus.lower() in line.lower():
                    relevant_lines.append(line)
            if relevant_lines:
                knowledge_content = "\n".join(relevant_lines[:20])

        # 导入 planner
        try:
            from planner import ShipLearnPlanner
        except ImportError:
            planner_path = SKILL_DIR / "planner.py"
            if planner_path.exists():
                import importlib.util
                spec = importlib.util.spec_from_file_location("planner", planner_path)
                planner_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(planner_module)
                ShipLearnPlanner = planner_module.ShipLearnPlanner
            else:
                return "错误: 无法加载 planner 模块"

        # 创建计划
        planner = ShipLearnPlanner()
        plan_name = focus or f"{topic}学习实践"

        plan_data = planner.create_plan(
            plan_name=plan_name,
            source_topic=topic,
            knowledge_content=knowledge_content,
            learning_goal=f"将{topic}主题中的知识转化为实际能力" if not focus else f"掌握并应用{focus}",
            duration_weeks=duration_weeks,
        )

        # 生成结果摘要
        lines = [
            f"## ✅ Ship-Learn-Next 计划已创建",
            "",
            f"**计划名称**: {plan_data['plan_name']}",
            f"**知识来源**: {plan_data['source_topic']}",
            f"**计划周期**: {plan_data['duration_weeks']} 周",
            f"**计划文件**: `{plan_data['plan_file']}`",
            "",
            "### 📋 迭代概览",
            "",
        ]

        for week in plan_data['weeks']:
            lines.append(f"**Week {week['number']}** ({week['start_date']} - {week['end_date']})")
            lines.append(f"- SHIP: {week['ship_task'][:60]}...")
            lines.append("")

        lines.extend([
            "### 🚀 下一步",
            "",
            "1. 查看完整计划文件",
            f"2. 开始 Week 1 的 SHIP 任务",
            f"3. 完成后使用 `track_iteration` 记录进度",
        ])

        return "\n".join(lines)

    except Exception as e:
        return f"创建计划失败: {type(e).__name__}: {e}"


@mcp.tool()
async def track_iteration(
    plan_id: str,
    week: int,
    ship_result: str,
    learn_reflection: str,
    next_adjustment: str = "",
) -> str:
    """记录 Ship-Learn-Next 计划的迭代执行结果.

    Args:
        plan_id: 计划ID（如 'Plan-Prompt工程-20260228' 或简写 'Prompt工程'）
        week: 周次（1-4）
        ship_result: SHIP 交付物描述（实际完成了什么）
        learn_reflection: LEARN 反思内容（什么有效/无效/发现/改进）
        next_adjustment: NEXT 调整建议（可选）

    Returns:
        记录结果

    Example:
        track_iteration(
            plan_id="Plan-Prompt工程-20260228",
            week=1,
            ship_result="完成了3个工作场景的Prompt优化，平均效率提升30%",
            learn_reflection="发现简洁的指令效果更好，复杂模板反而容易出错"
        )
    """
    try:
        # 导入 tracker
        try:
            from tracker import IterationTracker
        except ImportError:
            tracker_path = SKILL_DIR / "tracker.py"
            if tracker_path.exists():
                import importlib.util
                spec = importlib.util.spec_from_file_location("tracker", tracker_path)
                tracker_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(tracker_module)
                IterationTracker = tracker_module.IterationTracker
            else:
                return "错误: 无法加载 tracker 模块"

        tracker = IterationTracker()
        result = tracker.track_iteration(
            plan_id=plan_id,
            week=week,
            ship_result=ship_result,
            learn_reflection=learn_reflection,
            next_adjustment=next_adjustment,
        )

        if "error" in result:
            return f"记录失败: {result['error']}"

        # 获取最新状态
        status = tracker.get_plan_status(plan_id)

        lines = [
            f"## ✅ Week {week} 迭代已记录",
            "",
            f"**计划**: {plan_id}",
            f"**总体进度**: {status.get('progress', 'N/A')}",
            f"**状态**: {'已完成' if status.get('status') == 'completed' else '进行中'}",
            "",
            "### 📝 记录内容",
            "",
            f"**SHIP**: {ship_result[:100]}...",
            "",
            f"**LEARN**: {learn_reflection[:100]}...",
            "",
            "### 🚀 下一步",
            "",
        ]

        if week < 4:
            lines.append(f"继续 Week {week + 1} 的 SHIP 任务！")
        else:
            lines.append("恭喜完成整个计划！可以使用 `export_plan_to_ppt` 导出分享。")

        return "\n".join(lines)

    except Exception as e:
        return f"记录失败: {type(e).__name__}: {e}"


@mcp.tool()
async def export_plan_to_ppt(
    plan_id: str,
    style: str = "snoopy",
) -> str:
    """将 Ship-Learn-Next 计划导出为 PPT 分享文档.

    Args:
        plan_id: 计划ID（如 'Plan-Prompt工程-20260228'）
        style: 视觉风格（可选: snoopy, manga, oatmeal, cyberpunk 等）

    Returns:
        导出结果，包含 PPT 文件路径

    Example:
        export_plan_to_ppt(plan_id="Plan-Prompt工程-20260228", style="snoopy")
    """
    try:
        # 导入 exporter
        try:
            from exporter import PlanExporter
        except ImportError:
            exporter_path = SKILL_DIR / "exporter.py"
            if exporter_path.exists():
                import importlib.util
                spec = importlib.util.spec_from_file_location("exporter", exporter_path)
                exporter_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(exporter_module)
                PlanExporter = exporter_module.PlanExporter
            else:
                return "错误: 无法加载 exporter 模块"

        exporter = PlanExporter()
        result = exporter.export_to_ppt(
            plan_id=plan_id,
            style=style,
        )

        if "error" in result:
            return f"导出失败: {result['error']}"

        if result.get("success"):
            lines = [
                f"## ✅ PPT 导出成功！",
                "",
                f"**计划**: {plan_id}",
                f"**幻灯片数量**: {result['slide_count']} 页",
                f"**风格**: {result['style']}",
                f"**输出文件**: `{result['output_file']}`",
                "",
                "### 📊 PPT 包含内容",
                "",
                "1. 封面 - 计划名称和概述",
                "2. 学习目标",
                "3. 知识来源摘要",
                "4-7. Week 1-4 的迭代计划",
                "8. 行动号召",
                "",
                "可以直接用于分享和展示！",
            ]
            return "\n".join(lines)
        else:
            return "导出失败: 未知错误"

    except Exception as e:
        return f"导出失败: {type(e).__name__}: {e}"


@mcp.tool()
async def list_ship_plans() -> str:
    """列出所有 Ship-Learn-Next 实践计划.

    Returns:
        计划列表
    """
    try:
        # 导入 tracker
        try:
            from tracker import IterationTracker
        except ImportError:
            tracker_path = SKILL_DIR / "tracker.py"
            if tracker_path.exists():
                import importlib.util
                spec = importlib.util.spec_from_file_location("tracker", tracker_path)
                tracker_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(tracker_module)
                IterationTracker = tracker_module.IterationTracker
            else:
                return "错误: 无法加载 tracker 模块"

        tracker = IterationTracker()
        plans = tracker.list_active_plans()

        if not plans:
            return "暂无 Ship-Learn-Next 计划。使用 `create_ship_plan` 创建第一个计划！"

        lines = [
            f"## 📋 Ship-Learn-Next 计划列表 ({len(plans)} 个)",
            "",
            "| 计划名称 | 创建日期 | 进度 | 状态 |",
            "|---------|---------|------|------|",
        ]

        for plan in plans:
            status_emoji = "✅" if plan['status'] == 'completed' else "🔄"
            lines.append(f"| {plan['name']} | {plan['date']} | {plan['progress']} | {status_emoji} |")

        lines.extend([
            "",
            "### 💡 提示",
            "",
            "- 使用 `create_ship_plan` 创建新计划",
            "- 使用 `track_iteration` 记录进度",
            "- 使用 `export_plan_to_ppt` 导出分享",
        ])

        return "\n".join(lines)

    except Exception as e:
        return f"获取计划列表失败: {type(e).__name__}: {e}"


def main() -> None:
    """启动 MCP Server."""
    mcp.run()


if __name__ == "__main__":
    main()
