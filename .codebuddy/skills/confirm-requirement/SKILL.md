---
name: confirm-requirement
description: "需求文档确认与发布工具。当用户使用 /confirm_requirement 指令时，表示用户已确认当前需求文档为最终输出版，自动执行三项同步操作：(1) 同步到 iWiki 个人空间的工作文件夹；(2) 转化为 Excel 文件存入本地默认目录；(3) 在本地 work 文件夹中保留备份。适用场景：用户说 '/confirm_requirement'、'确认需求'、'需求文档定稿'、'发布需求文档'、'同步需求到 wiki 和 excel' 等。"
---

# 需求文档确认与发布（/confirm_requirement）

## 指令说明

`/confirm_requirement` 表示用户已确认当前需求文档为**最终输出版**，需要自动完成以下三项操作：

1. **同步到 iWiki** — 发布到个人空间的「工作」文件夹
2. **转化为 Excel** — 使用 md-to-excel 工具转换并存入默认目录
3. **本地备份** — 确认本地 MD 源文件已保存

## 执行流程

### 1. 确定源文件

- 如果用户指定了文件路径，使用指定路径
- 如果未指定，使用用户当前打开的 `.md` 文件
- 如果无法确定，询问用户

### 2. 同步到 iWiki

使用 iWiki MCP 工具，按以下规范执行：

- **目标位置**：个人空间 (spaceid: 4010703137) → 工作文件夹 (parentid: 4018520220)
- **文档类型**：MD
- **创建流程**（遵循双步写入规范）：
  1. `createDocument` 创建文档，body 传占位文本（非空）
  2. `saveDocument` 写入完整 Markdown 内容
  3. 如内容过长导致 JSON 解析失败，使用 `saveDocumentParts` 分批追加
- **去重逻辑**：如 iWiki work 文件夹下已存在同名文档，使用 `saveDocument` 更新内容而非重复创建

### 3. 转化为 Excel

使用 md-to-excel MCP 工具：

- **转换模式**：document（全文档结构化写入）
- **输出目录**：`g:\tianyishao\Moos-share\data\context\__created\work\to_excel\`
- **输出文件名**：与源 MD 文件同名，后缀改为 `.xlsx`

### 4. 完成报告

执行完成后，输出结构化报告：

```
✅ 需求文档已确认并发布

| 操作 | 状态 | 详情 |
|---|---|---|
| iWiki 同步 | ✅ | docid: XXXX，链接: https://iwiki.woa.com/pages/XXXX |
| Excel 转换 | ✅ | 输出: xxx.xlsx |
| 本地 MD | ✅ | 路径: xxx.md |
```

## 注意事项

- 每次执行前先读取最新的 MD 文件内容，确保同步的是最新版本
- iWiki 创建文档时必须遵循「先创建后写入」的双步规范，避免 JSON ProseMirror 渲染问题
- Excel 转换使用 document 模式，保留层级缩进布局、标题灰底加粗、内容浅绿底等样式
- 如果文档内容较长，saveDocument 可能因 JSON 解析失败，此时改用 saveDocumentParts 分段追加
