# WOW 本地化配置元数据

## 文件路径

| 项目 | 路径/值 |
|---|---|
| 本地 MD 源文件 | `g:\tianyishao\Moos-share\data\context\__created\work\wow_localization_config.md` |
| Excel 输出目录 | `g:\tianyishao\Moos-share\data\context\__created\work\to_excel\` |
| Excel 文件名 | `wow_localization_config.xlsx` |

## iWiki 配置

| 项目 | 值 |
|---|---|
| 文档标题 | WOW智能助手-本地化配置记录 |
| docid | 4018676062 |
| spaceid | 4010703137 |
| parentid | 4018520220 |
| contenttype | MD |

## ID 分配规则

- 所有 ID 为 8 位数字，格式为 `97XXXXXX`
- 当前已使用的 ID 段：
  - `97000001` ~ `97000052`：WOW小助手/WoW小助手 系列（早期）
  - `97001053` ~ `97001115`：WOW智能助手-通用文本 系列
- 新增条目时，从当前最大 ID + 1 开始递增分配
- 当前最大 ID 记录在 memory 中，每次更新后同步更新 memory

## 分类命名规范

已有分类：
- `WOW小助手-通用文案`
- `WOW小助手-组合拼装生成`
- `WoW小助手-通用文案`
- `WOW智能助手-通用文本`

新增条目时，用户可指定分类，若未指定则默认使用 `WOW智能助手-通用文本`。

## 表格格式

Markdown 表格固定 4 列：

```
| ID | 文案内容 | 分类 | 负责人 |
```

- **ID**：8 位数字
- **文案内容**：本地化显示文本，可包含占位符 `{0}` `{1}` 或 `%s`，可包含 `\n` 换行符
- **分类**：功能模块分类
- **负责人**：默认 `tianyishao`
