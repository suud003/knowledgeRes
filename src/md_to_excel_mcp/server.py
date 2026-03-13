"""MCP Server - Markdown 转 Excel 转换服务.

将 Markdown 文档中的表格、标题、列表、代码块等结构化内容
智能转换为格式精美的 Excel 文件（.xlsx）。

支持三种模式：
1. tables 模式 — 提取所有表格到多个 Sheet
2. document 模式 — 全文档结构化写入单 Sheet
3. auto 模式 — 自动判断最佳策略

工具列表：
- md_to_excel: 将 Markdown 文件/内容转换为 Excel
- md_tables_to_excel: 从 Markdown 中提取表格并写入 Excel
- parse_md_structure: 解析 Markdown 文档结构（不生成文件，返回结构信息）
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# 将 md_to_excel 脚本目录加入路径
# __file__ 位于 src/md_to_excel_mcp/server.py，需要向上 3 层到项目根目录
_SCRIPT_DIR = Path(__file__).parent.parent.parent / ".codebuddy" / "skills" / "md-to-excel" / "scripts"
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from md_to_excel import (
    parse_md_structure as _parse_md_structure,
    parse_md_tables as _parse_md_tables,
    write_document_to_excel,
    write_structured_to_excel,
    write_tables_to_excel,
)

# 默认输出目录：所有转换后的 Excel 文件默认存放到此目录
_DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "context" / "__created" / "work" / "to_excel"

# 创建 MCP Server
mcp = FastMCP("md-to-excel")


def _resolve_output_path(input_path: str | None, output_path: str | None) -> Path:
    """解析输出文件路径.

    优先使用用户指定的 output_path；
    若未指定，则将文件输出到默认目录（data/context/__created/work/to_excel/）；
    若连 input_path 都没有，则在默认目录生成临时文件。
    """
    if output_path:
        return Path(output_path)

    # 确保默认输出目录存在
    _DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if input_path:
        # 使用输入文件名，但输出到默认目录
        return _DEFAULT_OUTPUT_DIR / Path(input_path).with_suffix(".xlsx").name
    # 生成临时文件到默认目录
    tmp = tempfile.NamedTemporaryFile(
        suffix=".xlsx", delete=False, prefix="md2excel_", dir=str(_DEFAULT_OUTPUT_DIR)
    )
    tmp.close()
    return Path(tmp.name)


@mcp.tool()
async def md_to_excel(
    mode: str = "auto",
    input_path: str | None = None,
    md_content: str | None = None,
    output_path: str | None = None,
) -> str:
    """将 Markdown 文件或内容转换为格式精美的 Excel 文件.

    支持三种模式：
    - auto（默认）：自动判断，有表格则提取表格，否则全文档结构化
    - tables：仅提取 Markdown 中的表格，每个表格一个 Sheet
    - document：全文档结构化写入单 Sheet，保留标题层级、段落、列表、代码块等

    Args:
        mode: 转换模式，可选 "auto"、"tables"、"document"
        input_path: 输入 Markdown 文件的绝对路径（与 md_content 二选一）
        md_content: 直接传入的 Markdown 文本内容（与 input_path 二选一）
        output_path: 输出 Excel 文件的绝对路径（可选，默认与输入文件同名 .xlsx）

    Returns:
        转换结果说明，包含输出文件路径和转换详情
    """
    # 参数校验
    if not input_path and not md_content:
        return "❌ 错误：必须提供 input_path（文件路径）或 md_content（文本内容）之一"

    if mode not in ("auto", "tables", "document"):
        return f"❌ 错误：不支持的模式 '{mode}'，请使用 auto、tables 或 document"

    # 读取 Markdown 内容
    if input_path:
        p = Path(input_path)
        if not p.exists():
            return f"❌ 错误：文件不存在 - {input_path}"
        if not p.suffix.lower() in (".md", ".markdown", ".txt"):
            return f"⚠️ 警告：文件后缀为 {p.suffix}，可能不是 Markdown 文件，继续尝试转换..."
        try:
            content = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = p.read_text(encoding="gbk")
            except Exception as e:
                return f"❌ 错误：无法读取文件 - {e}"
    else:
        content = md_content  # type: ignore[assignment]

    if not content or not content.strip():
        return "❌ 错误：Markdown 内容为空"

    # 解析输出路径
    out = _resolve_output_path(input_path, output_path)

    # 执行转换
    try:
        result_path = write_structured_to_excel(content, str(out), mode=mode)

        # 统计信息
        tables = _parse_md_tables(content)
        blocks = _parse_md_structure(content)
        table_count = len(tables)
        heading_count = sum(1 for b in blocks if b["type"] == "heading")
        para_count = sum(1 for b in blocks if b["type"] == "paragraph")
        list_count = sum(1 for b in blocks if b["type"] == "list")
        code_count = sum(1 for b in blocks if b["type"] == "code")

        # 判断实际使用的模式
        actual_mode = mode
        if mode == "auto":
            actual_mode = "tables" if table_count > 0 else "document"

        lines = [
            "✅ Markdown → Excel 转换完成！",
            "",
            f"📄 源文件: {input_path or '（直接输入内容）'}",
            f"📊 输出文件: {result_path}",
            f"📋 模式: {mode}" + (f" → 实际使用 {actual_mode}" if mode == "auto" else ""),
            "",
            "📊 内容统计:",
            f"  - 标题: {heading_count} 个",
            f"  - 段落: {para_count} 个",
            f"  - 表格: {table_count} 个",
            f"  - 列表: {list_count} 个",
            f"  - 代码块: {code_count} 个",
        ]

        if actual_mode == "tables" and table_count > 0:
            lines.append("")
            lines.append("📑 Sheet 列表:")
            for i, t in enumerate(tables, 1):
                lines.append(f"  {i}. {t['title']} ({len(t['rows'])} 行 × {len(t['headers'])} 列)")

        return "\n".join(lines)

    except ValueError as e:
        return f"❌ 转换失败：{e}"
    except Exception as e:
        return f"❌ 转换失败：{type(e).__name__}: {e}"


@mcp.tool()
async def md_tables_to_excel(
    input_path: str | None = None,
    md_content: str | None = None,
    output_path: str | None = None,
) -> str:
    """从 Markdown 中提取所有表格并写入 Excel（每个表格一个 Sheet）.

    这是 md_to_excel(mode="tables") 的快捷方式，
    专门用于只需要提取表格数据的场景。

    Args:
        input_path: 输入 Markdown 文件的绝对路径（与 md_content 二选一）
        md_content: 直接传入的 Markdown 文本内容（与 input_path 二选一）
        output_path: 输出 Excel 文件的绝对路径（可选）

    Returns:
        提取结果说明，包含表格数量和 Sheet 信息
    """
    # 参数校验
    if not input_path and not md_content:
        return "❌ 错误：必须提供 input_path（文件路径）或 md_content（文本内容）之一"

    # 读取内容
    if input_path:
        p = Path(input_path)
        if not p.exists():
            return f"❌ 错误：文件不存在 - {input_path}"
        try:
            content = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = p.read_text(encoding="gbk")
    else:
        content = md_content  # type: ignore[assignment]

    # 提取表格
    tables = _parse_md_tables(content)
    if not tables:
        return "❌ Markdown 中未找到任何表格。建议使用 md_to_excel(mode='document') 进行全文档转换。"

    # 输出路径
    out = _resolve_output_path(input_path, output_path)

    try:
        result_path = write_tables_to_excel(tables, str(out))

        lines = [
            "✅ 表格提取完成！",
            "",
            f"📄 源文件: {input_path or '（直接输入内容）'}",
            f"📊 输出文件: {result_path}",
            f"📋 共提取 {len(tables)} 个表格",
            "",
            "📑 Sheet 列表:",
        ]
        for i, t in enumerate(tables, 1):
            lines.append(f"  {i}. {t['title']} ({len(t['rows'])} 行 × {len(t['headers'])} 列)")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ 提取失败：{type(e).__name__}: {e}"


@mcp.tool()
async def parse_md_structure(
    input_path: str | None = None,
    md_content: str | None = None,
) -> str:
    """解析 Markdown 文档结构（不生成文件，仅返回结构信息）.

    适用于需要预览文档结构、判断转换模式，或调试内容解析的场景。

    Args:
        input_path: 输入 Markdown 文件的绝对路径（与 md_content 二选一）
        md_content: 直接传入的 Markdown 文本内容（与 input_path 二选一）

    Returns:
        文档结构概览，包含各类型内容块的统计和详情
    """
    if not input_path and not md_content:
        return "❌ 错误：必须提供 input_path（文件路径）或 md_content（文本内容）之一"

    if input_path:
        p = Path(input_path)
        if not p.exists():
            return f"❌ 错误：文件不存在 - {input_path}"
        try:
            content = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = p.read_text(encoding="gbk")
    else:
        content = md_content  # type: ignore[assignment]

    blocks = _parse_md_structure(content)
    tables = _parse_md_tables(content)

    if not blocks:
        return "❌ Markdown 内容为空或无法解析"

    # 统计
    type_counts: dict[str, int] = {}
    for b in blocks:
        t = b["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    lines = [
        "📋 Markdown 文档结构解析",
        "",
        "📊 内容统计:",
    ]
    type_names = {
        "heading": "标题",
        "paragraph": "段落",
        "table": "表格",
        "list": "列表",
        "code": "代码块",
    }
    for t, count in type_counts.items():
        lines.append(f"  - {type_names.get(t, t)}: {count} 个")

    # 推荐模式
    lines.append("")
    if tables:
        lines.append(f"💡 推荐模式: tables（检测到 {len(tables)} 个表格）")
    else:
        lines.append("💡 推荐模式: document（未检测到表格，适合全文档转换）")

    # 标题大纲
    headings = [b for b in blocks if b["type"] == "heading"]
    if headings:
        lines.append("")
        lines.append("📑 文档大纲:")
        for h in headings:
            indent = "  " * (h.get("level", 1) - 1)
            lines.append(f"  {indent}{'#' * h.get('level', 1)} {h['content']}")

    # 表格概览
    if tables:
        lines.append("")
        lines.append("📊 表格概览:")
        for i, t in enumerate(tables, 1):
            lines.append(f"  {i}. {t['title']} ({len(t['rows'])} 行 × {len(t['headers'])} 列)")
            if t["headers"]:
                lines.append(f"     列: {', '.join(t['headers'][:5])}" +
                           ("..." if len(t["headers"]) > 5 else ""))

    return "\n".join(lines)


def main() -> None:
    """MCP 服务启动入口."""
    mcp.run()


if __name__ == "__main__":
    main()
