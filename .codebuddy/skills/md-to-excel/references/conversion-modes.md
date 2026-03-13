# Markdown → Excel 转换模式参考

## 三种转换模式

### 1. `tables` 模式 — 表格提取

从 Markdown 中提取所有表格，每个表格写入单独的 Sheet。

**适用场景**：
- Markdown 中包含多个数据表格
- 只需要表格数据，不需要其他文本内容
- 需要在 Excel 中进行数据分析、筛选、排序

**输出特性**：
- 每个表格一个 Sheet，Sheet 名取自表格上方最近的标题
- 表头行冻结 + 自动筛选
- 自动列宽适配

**示例 Markdown**：
```markdown
## 用户统计

| 姓名 | 部门 | 年龄 |
|------|------|------|
| 张三 | 研发 | 28   |
| 李四 | 产品 | 32   |

## 项目列表

| 项目名 | 状态 | 负责人 |
|--------|------|--------|
| A      | 进行中 | 张三 |
```

→ 输出：2 个 Sheet（"用户统计"、"项目列表"），各包含对应表格。

---

### 2. `document` 模式 — 全文档结构化

将整篇 Markdown 文档按结构写入单个 Sheet。

**适用场景**：
- 需要保留文档的完整结构（标题层级、段落、列表等）
- 需要在 Excel 中审阅或批注文档内容
- 需要基于文档结构做数据处理

**输出列结构**：

| 类型 | 层级 | 内容 |
|------|------|------|
| 标题 | H1   | 文档标题 |
| 段落 |      | 正文内容... |
| 列表项 | • | 第一项 |
| 表格 | 3行×2列 | (表头写在第3列往后) |
| 代码块 | python | def hello(): ... |

**样式特性**：
- 标题按层级使用不同字号和颜色
- 代码块使用等宽字体 + 灰色背景
- 表格以内嵌方式写入，保留表头样式

---

### 3. `auto` 模式 — 智能判断（默认）

自动判断最佳转换策略：
- 如果 Markdown 中包含表格 → 使用 `tables` 模式
- 如果没有表格 → 使用 `document` 模式

大多数情况下使用此模式即可。

---

## 常见操作示例

### 读取 Markdown 文件并转换

```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from md_to_excel import write_structured_to_excel

md_content = Path("input.md").read_text(encoding="utf-8")
output = write_structured_to_excel(md_content, "output.xlsx", mode="auto")
```

### 手动构造表格数据并写入

```python
from md_to_excel import write_tables_to_excel

tables = [
    {
        "title": "统计数据",
        "headers": ["指标", "数值", "同比"],
        "rows": [
            ["日活", "100万", "+5%"],
            ["月活", "500万", "+3%"],
        ]
    }
]
write_tables_to_excel(tables, "stats.xlsx")
```

### 批量转换多个 Markdown 文件

```python
from pathlib import Path
from md_to_excel import write_structured_to_excel

for md_file in Path("docs/").glob("*.md"):
    output = md_file.with_suffix(".xlsx")
    content = md_file.read_text(encoding="utf-8")
    write_structured_to_excel(content, output)
    print(f"✅ {md_file.name} → {output.name}")
```

## 样式自定义

脚本中的样式常量定义在文件顶部，可按需修改：

| 常量 | 说明 | 默认值 |
|------|------|--------|
| `HEADER_FILL` | 表头背景色 | 蓝色 #4472C4 |
| `HEADER_FONT` | 表头字体 | 微软雅黑 11pt 白色加粗 |
| `BODY_FONT` | 正文字体 | 微软雅黑 10pt |
| `CODE_FONT` | 代码字体 | Consolas 9pt |
| `CODE_FILL` | 代码块背景 | 浅灰 #F5F5F5 |
| `THIN_BORDER` | 边框样式 | 浅灰细线 |
