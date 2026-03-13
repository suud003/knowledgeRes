---
name: wow-localization
description: "WOW 智能助手本地化配置管理工具。用于管理 WOW 智能助手的本地化文案条目，支持新增和替换两种操作模式。当用户提供需要本地化的文本内容时（如 UI 文案、提示语、功能描述等），自动分析需求，分配 ID，并同步更新到三个位置：本地 Markdown 源文件、Excel 导出文件、iWiki 文档。支持批量添加多条文案，支持替换已有的'字段占用'占位文本。适用场景：用户说'添加本地化'、'新增本地化文案'、'配置本地化'、'本地化文本'、'加个本地化条目'、'需要配置文案'、'多语言文案'、提供一批需要本地化的文本、或需要替换占位文本等。"
---

# WOW 本地化配置管理

## 概述

管理 WOW 智能助手的本地化文案配置，每条文案对应一个唯一 ID，用于客户端多语言显示。配置数据三端同步：本地 MD → Excel → iWiki。

关键配置信息见 [config-metadata.md](references/config-metadata.md)。

## 触发条件

当用户提供需要本地化的文本时触发，典型场景：
- 直接给出一批需要配置的显示文案
- 描述一个功能需求，其中涉及需要本地化的 UI 文本
- 要求替换已有的"字段占用"占位条目

## 操作模式

### 模式 A：新增条目

用户提供新的本地化文案，执行：
1. 从 memory 获取当前最大 ID，新条目 ID = 最大 ID + 1 递增
2. 追加到本地 MD 表格末尾
3. 重新生成 Excel
4. 同步更新 iWiki 文档

### 模式 B：替换"字段占用"条目

当用户指定要替换内容为"字段占用"的条目时：
1. 读取本地 MD 文件，定位所有"字段占用"条目
2. 按顺序用新文案替换"字段占用"的文案内容，保留原 ID 不变
3. 若新文案数量 > 可替换的"字段占用"数量，剩余的按模式 A 新增
4. 更新分类（如用户指定）
5. 重新生成 Excel 和同步 iWiki

### 模式判断规则

- 用户明确说"替换字段占用" → 模式 B
- 用户只提供文案未提及替换 → 优先询问是否替换现有"字段占用"条目，若无可替换项则自动走模式 A
- 存在"字段占用"条目时，主动告知用户并询问意向

## 执行流程

### Step 1：分析用户需求

从用户提供的文本或需求描述中提取本地化条目：

- **文案内容**：用户提供的显示文本
- **分类**：用户指定的分类，若未指定默认 `WOW智能助手-通用文本`
- **负责人**：默认 `tianyishao`
- **占位符处理**：如文案中包含动态变量，使用 `{0}`、`{1}` 等格式（与现有条目保持一致）

输出提取结果表格供用户确认：

```
📋 已识别以下本地化条目：

| # | 操作 | ID | 文案内容 | 分类 |
|---|---|---|---|---|
| 1 | 新增 | 97001116 | xxx | WOW智能助手-通用文本 |
| 2 | 替换 | 97001115 | yyy（原：字段占用） | WOW智能助手-通用文本 |

是否确认添加？
```

**重要**：必须在用户确认后才执行写入操作。

### Step 2：更新本地 MD 文件

读取 `g:\tianyishao\Moos-share\data\context\__created\work\wow_localization_config.md`：

- **新增**：在表格末尾追加新行
- **替换**：定位目标行，将"字段占用"替换为新的文案内容，可同时更新分类

使用 `replace_in_file` 或 `edit_file` 编辑。编辑前必须先 `read_file` 获取最新内容。

### Step 3：重新生成 Excel

使用 md-to-excel MCP 工具：

```
serverName: md-to-excel
toolName: md_tables_to_excel
arguments:
  input_path: g:\tianyishao\Moos-share\data\context\__created\work\wow_localization_config.md
  output_path: g:\tianyishao\Moos-share\data\context\__created\work\to_excel\wow_localization_config.xlsx
```

### Step 4：同步 iWiki

使用 iWiki MCP 的 `saveDocument` 更新文档（docid: 4018676062）：

- 读取更新后的本地 MD 文件全部内容
- 调用 `saveDocument`，将完整 Markdown 内容写入 iWiki
- **注意**：不需要 createDocument，文档已存在，直接 saveDocument 更新

```
serverName: iWiki
toolName: saveDocument
arguments:
  docid: 4018676062
  title: "WOW智能助手-本地化配置记录"
  body: <完整的 Markdown 内容>
```

### Step 5：更新 Memory

调用 `update_memory` 更新记忆中的最大 ID 值（memory ID: 4ouwn5mi）。

### Step 6：输出报告

```
✅ 本地化配置已更新

| 操作 | 数量 | 详情 |
|---|---|---|
| 新增 | X 条 | ID: 97001116 ~ 97001118 |
| 替换 | Y 条 | ID: 97001115（原"字段占用"） |

| 同步状态 | 结果 |
|---|---|
| 本地 MD | ✅ 已更新 |
| Excel | ✅ 已重新生成 |
| iWiki | ✅ 已同步（docid: 4018676062） |

当前最大 ID：97001118
```

## 注意事项

1. **先确认再执行**：提取条目后必须展示并等用户确认，避免误操作
2. **ID 不可回收**：已使用的 ID 即使对应条目被删除也不再复用
3. **编辑前必须读文件**：每次编辑前先 read_file 获取最新内容，避免冲突
4. **长文案处理**：文案中如包含换行符，使用 `\n` 表示，保持 Markdown 表格单行格式
5. **特殊字符**：文案中可能包含 HTML 标签（如 `<a>`）、占位符（`{0}`、`%s`），原样保留不转义
6. **iWiki 同步失败兜底**：如 iWiki MCP 不可用，先完成本地操作，提示用户后续手动同步或等服务恢复
7. **分类一致性**：建议优先使用已有的分类名称，避免创建过多新分类
