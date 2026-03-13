---
name: md-to-excel
description: "Markdown 文档适配到 Excel 的转换工具。将 Markdown 中的表格、标题、列表、代码块等结构化内容智能转换为格式精美的 Excel 文件（.xlsx）。支持三种模式：(1) tables 模式 — 提取所有表格到多个 Sheet，(2) document 模式 — 全文档结构化写入单 Sheet，(3) auto 自动判断。适用场景：用户说'转成 Excel'、'导出 Excel'、'MD 转 xlsx'、'表格导出'、'Markdown 导出到 Excel'、'把这个文档转成 Excel'、'提取表格到 Excel'、将需求文档/数据表格/统计报告等 Markdown 内容适配到 Excel 格式等。"
---

# Markdown → Excel 转换

将 Markdown 文档内容智能转换为格式精美的 Excel 文件。

## 核心能力

1. **表格提取**：自动识别 Markdown 中的所有表格，每个表格写入独立 Sheet
2. **全文档转换**：按标题层级缩进布局，不显示类型/层级属性，同层级标题在同一列，下级内容自动偏移
3. **样式美化**：自动表头着色、字体适配、列宽自适应
4. **智能判断**：auto 模式根据内容自动选择最佳转换策略

### document 模式布局规则

- **不显示类型和层级属性**：不输出"标题"、"列表项"、"H2"等元信息列
- **标题按层级占列**：H1 在 A 列、H2 在 B 列、H3 在 C 列...同层级标题始终在同一列
- **内容自动偏移**：标题下的内容（段落、列表、表格、代码）自动往后偏移一列，体现从属关系
- **多行文字逐行写入**：段落中的多行文字每行独立占 Excel 一行，不合并

## 依赖

- `openpyxl`（项目已有，无需额外安装）

## 执行流程

### 第一步：确定输入源

1. **用户指定 Markdown 文件路径** → 使用 `read_file` 读取内容
2. **用户提供 Markdown 文本** → 直接使用文本内容
3. **用户要求转换当前打开的文件** → 读取当前文件

### 第二步：确定转换模式

- 用户明确指定了 "只要表格" → `tables` 模式
- 用户明确指定了 "全文档" → `document` 模式
- 用户未指定或说 "转 Excel" → `auto` 模式（有表格则提取表格，无表格则全文档）
- 详细模式说明见 `references/conversion-modes.md`

### 第三步：执行转换

使用 `scripts/md_to_excel.py` 脚本中的函数。

**方式一：直接调用 Python 函数（推荐）**

```python
import sys
from pathlib import Path

# 加载脚本
sys.path.insert(0, str(Path("SKILL_DIR/scripts")))
from md_to_excel import write_structured_to_excel, parse_md_tables, write_tables_to_excel

# 方式 A：自动模式
md_content = Path("input.md").read_text(encoding="utf-8")
result = write_structured_to_excel(md_content, "output.xlsx", mode="auto")

# 方式 B：仅表格
tables = parse_md_tables(md_content)
write_tables_to_excel(tables, "output.xlsx")
```

> 注意：`SKILL_DIR` 替换为 Skill 的实际绝对路径。

**方式二：命令行调用**

```bash
python scripts/md_to_excel.py input.md --output output.xlsx --mode auto
```

### 默认输出目录

所有转换生成的 Excel 文件**默认存放到**：

```
data/context/__created/work/to_excel/
```

- 当用户未指定 `output_path` 时，自动将文件输出到此目录
- MCP 服务中 `_resolve_output_path` 已内置此逻辑，无需手动指定
- 如果用户明确指定了输出路径，则以用户指定的路径为准

### 第四步：输出确认

转换完成后，反馈给用户：

```
✅ Markdown → Excel 转换完成

📄 源文件: input.md
📊 输出文件: data/context/__created/work/to_excel/output.xlsx
📋 模式: auto (提取了 N 个表格)
📂 Sheet 列表: Sheet1, Sheet2, ...
```

## 特殊处理

### 表格中的特殊内容
- Markdown 链接 `[text](url)` → 自动提取为纯文本 `text`
- 粗体 `**text**`、斜体 `*text*` → 自动清除格式符号，保留纯文本
- 行内代码 `` `code` `` → 自动去除反引号
- 删除线 `~~text~~` → 自动清除格式符号
- 引用标记 `>` → 自动去除
- HTML 标签（如 `<br>`、`<b>` 等） → 自动去除
- 空单元格 → 写入空字符串

### Sheet 名称
- 自动取表格上方最近的标题作为 Sheet 名
- 自动去除 Excel 不允许的字符（`[]:\/?*`）
- 自动截断为 31 字符（Excel 限制）
- 重名自动追加序号

### 中文适配
- 默认字体使用"微软雅黑"
- 列宽计算考虑中文字符（占 2 个宽度单位）

## 错误处理

| 错误 | 处理方式 |
|------|---------|
| 文件不存在 | 提示用户检查路径 |
| Markdown 中无表格（tables 模式） | 提示切换到 document 模式 |
| Markdown 内容为空 | 提示用户检查文件内容 |
| 输出路径无权限 | 提示用户检查目录权限 |
