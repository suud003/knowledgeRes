"""CLI 命令行界面."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pa.config import Config, load_config
from pa.router.engine import RouterEngine

console = Console()


def print_banner() -> None:
    """打印欢迎横幅."""
    banner = """
╔═══════════════════════════════════════════╗
║   Personal Assistant - 个人智能助手        ║
║   Powered by Claude Code                  ║
╚═══════════════════════════════════════════╝
    """
    console.print(banner, style="cyan")


@click.group()
@click.option("--config", "-c", type=click.Path(), help="配置文件路径")
@click.pass_context
def cli(ctx: click.Context, config: str | None) -> None:
    """个人智能助手 CLI - 管理和同步个人 Context 数据."""
    ctx.ensure_object(dict)

    try:
        cfg = load_config(config)
        ctx.obj["config"] = cfg
    except FileNotFoundError as e:
        console.print(f"[red]错误: {e}[/red]")
        console.print("\n请复制 config.example.yaml 为 config.yaml 并填入配置:")
        console.print("  cp config.example.yaml config.yaml")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]加载配置失败: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """查看当前状态."""
    print_banner()

    config: Config = ctx.obj["config"]

    # 配置信息
    table = Table(title="配置信息")
    table.add_column("项目", style="cyan")
    table.add_column("值", style="green")

    table.add_row("飞书 App ID", config.feishu.app_id[:10] + "..." if config.feishu.app_id else "未配置")
    table.add_row("飞书数据源", str(len(config.feishu.bases)))
    table.add_row("主题数量", str(len(config.context.get_all_topics())))
    table.add_row("原始数据目录", config.sync.raw_dir)
    table.add_row("Context 目录", config.sync.context_dir)

    console.print(table)

    # 数据目录状态
    console.print("\n")
    table2 = Table(title="数据目录状态")
    table2.add_column("目录", style="cyan")
    table2.add_column("状态", style="green")
    table2.add_column("文件数")

    raw_dir = Path(config.sync.raw_dir)
    context_dir = Path(config.sync.context_dir)

    raw_exists = raw_dir.exists()
    context_exists = context_dir.exists()

    raw_count = len(list(raw_dir.rglob("*"))) if raw_exists else 0
    context_count = len(list(context_dir.rglob("*.md"))) if context_exists else 0

    table2.add_row(
        "原始数据",
        "[green]存在[/green]" if raw_exists else "[red]不存在[/red]",
        str(raw_count),
    )
    table2.add_row(
        "Context",
        "[green]存在[/green]" if context_exists else "[red]不存在[/red]",
        str(context_count),
    )

    console.print(table2)

    # 主题列表
    console.print("\n")
    table3 = Table(title="主题配置")
    table3.add_column("Key", style="cyan")
    table3.add_column("名称", style="green")
    table3.add_column("描述")

    for key, topic in config.context.get_all_topics().items():
        table3.add_row(key, topic.name, topic.description[:30] + "...")

    console.print(table3)


@cli.command()
@click.option("--source", "-s", help="指定数据源（如 feishu）")
@click.option("--dry-run", is_flag=True, help="试运行，不实际写入文件")
@click.pass_context
def sync(ctx: click.Context, source: str | None, dry_run: bool) -> None:
    """执行数据同步."""
    print_banner()

    config: Config = ctx.obj["config"]

    async def do_sync() -> None:
        all_records: list[dict[str, Any]] = []

        # 飞书同步
        if not source or source == "feishu":
            from pa.collectors.feishu import FeishuCollector

            console.print("[cyan]正在同步飞书数据源...[/cyan]")

            for base_config in config.feishu.bases:
                console.print(f"  同步: {base_config['name']}...", end=" ")

                try:
                    collector = FeishuCollector(
                        name=base_config["name"],
                        raw_dir=Path(config.sync.raw_dir) / "feishu",
                        app_id=config.feishu.app_id,
                        app_secret=config.feishu.app_secret,
                        app_token=base_config["app_token"],
                        table_id=base_config["table_id"],
                        field_mapping=base_config.get("fields"),
                    )
                    records = await collector.collect()

                    # 添加默认主题信息
                    default_topic = base_config.get("default_topic")
                    if default_topic:
                        for r in records:
                            r["default_topic"] = default_topic

                    all_records.extend(records)
                    console.print(f"[green]OK[/green] ({len(records)} 条)")
                except Exception as e:
                    console.print(f"[red]FAIL {e}[/red]")

        # Flomo 同步
        if not source or source == "flomo":
            from pa.collectors.flomo import FlomoCollector

            console.print("[cyan]正在同步 Flomo 数据源...[/cyan]")

            flomo_html = Path(config.sync.raw_dir) / "flomo" / "游方的笔记.html"
            if flomo_html.exists():
                console.print(f"  同步: Flomo 笔记...", end=" ")

                try:
                    collector = FlomoCollector(
                        name="flomo_notes",
                        raw_dir=Path(config.sync.raw_dir) / "flomo",
                        html_file=flomo_html,
                    )
                    records = await collector.collect()
                    all_records.extend(records)
                    console.print(f"[green]OK[/green] ({len(records)} 条)")
                except Exception as e:
                    console.print(f"[red]FAIL {e}[/red]")
            else:
                console.print(f"  [yellow]跳过: Flomo HTML 文件不存在于 {flomo_html}[/yellow]")

        if not all_records:
            console.print("[yellow]未获取到任何数据[/yellow]")
            return

        console.print(f"\n[cyan]共获取 {len(all_records)} 条记录[/cyan]")

        if dry_run:
            console.print("[yellow]试运行模式，跳过路由和写入[/yellow]")
            return

        # 路由数据
        console.print("[cyan]正在路由数据到主题...[/cyan]")
        router = RouterEngine(config)
        routed = router.route_batch(all_records)

        # 显示路由结果
        table = Table(title="路由结果")
        table.add_column("主题", style="cyan")
        table.add_column("记录数", style="green")

        for topic_key, records in routed.items():
            topic_config = config.context.get_all_topics().get(topic_key)
            topic_name = topic_config.name if topic_config else topic_key
            if records:
                table.add_row(topic_name, str(len(records)))

        console.print(table)

        # 写入文件
        console.print("[cyan]正在写入 Context 文件...[/cyan]")
        context_dir = Path(config.sync.context_dir)
        written_files = router.write_context_files(routed, context_dir)

        console.print(f"[green]OK - 写入完成: {len(written_files)} 个文件[/green]")
        for f in written_files:
            console.print(f"  - {f}")

    asyncio.run(do_sync())


@cli.command()
@click.option("--topic", "-t", help="指定主题查看")
@click.pass_context
def view(ctx: click.Context, topic: str | None) -> None:
    """查看 Context 内容."""
    config: Config = ctx.obj["config"]
    context_dir = Path(config.sync.context_dir)

    if not context_dir.exists():
        console.print("[red]Context 目录不存在，请先运行 sync 命令[/red]")
        return

    if topic:
        # 查看指定主题
        topic_dir = context_dir / topic
        if not topic_dir.exists():
            console.print(f"[red]主题 '{topic}' 不存在[/red]")
            return

        files = sorted(topic_dir.glob("*.md"), reverse=True)
        if not files:
            console.print(f"[yellow]主题 '{topic}' 暂无内容[/yellow]")
            return

        # 显示最新文件内容
        with open(files[0], "r", encoding="utf-8") as f:
            content = f.read()

        console.print(Panel(content, title=f"主题: {topic}", border_style="cyan"))
    else:
        # 列出所有主题
        table = Table(title="Context 内容概览")
        table.add_column("主题", style="cyan")
        table.add_column("文件数", style="green")
        table.add_column("最新文件", style="yellow")

        for topic_key in config.context.get_all_topics().keys():
            topic_dir = context_dir / topic_key
            if not topic_dir.exists():
                continue

            files = list(topic_dir.glob("*.md"))
            if files:
                latest = max(files, key=lambda f: f.stat().st_mtime)
                table.add_row(
                    topic_key,
                    str(len(files)),
                    latest.name,
                )

        console.print(table)


@cli.command()
@click.option("--host", default="127.0.0.1", help="监听地址")
@click.option("--port", default=8000, help="监听端口")
@click.option("--transport", default="stdio", type=click.Choice(["stdio", "sse"]), help="传输方式")
def serve(host: str, port: int, transport: str) -> None:
    """启动 MCP Server."""
    print_banner()

    console.print(f"[cyan]启动 MCP Server...[/cyan]")
    console.print(f"  传输方式: {transport}")

    if transport == "sse":
        console.print(f"  监听地址: {host}:{port}")

    # 导入并启动 server
    from pa.mcp_server import main

    if transport == "stdio":
        main()
    else:
        # 对于SSE传输，需要设置环境变量
        import os
        os.environ["MCP_TRANSPORT"] = "sse"
        os.environ["MCP_HOST"] = host
        os.environ["MCP_PORT"] = str(port)
        main()


@cli.command()
def init() -> None:
    """初始化项目配置."""
    print_banner()

    config_path = Path("config.yaml")

    if config_path.exists():
        if not click.confirm("配置文件已存在，是否覆盖?"):
            console.print("[yellow]已取消[/yellow]")
            return

    # 复制示例配置
    example_path = Path("config.example.yaml")
    if example_path.exists():
        import shutil

        shutil.copy(example_path, config_path)
        console.print(f"[green]OK - 已创建配置文件: {config_path}[/green]")
        console.print("\n[cyan]请编辑 config.yaml 填入你的配置:[/cyan]")
        console.print("  - 飞书 App ID 和 App Secret")
        console.print("  - 多维表格配置")
        console.print("  - Context 主题配置（可选）")
    else:
        console.print("[red]未找到 config.example.yaml[/red]")


def main() -> None:
    """CLI 入口."""
    cli()
