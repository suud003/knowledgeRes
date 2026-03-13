# /confirm_requirement [文件路径]

## 功能
确认需求文档为最终输出版，自动执行三项同步操作：同步到 iWiki、转化为 Excel、本地备份确认。

## 参数
- `文件路径`（可选）：需求文档的 MD 文件路径。不传则自动使用当前打开的 `.md` 文件

## 执行步骤

1. **加载 Skill**：调用 `use_skill` 加载 `confirm-requirement` Skill 获取完整工作流指引
2. **确定源文件**：如果用户指定了文件路径则使用指定路径，否则使用当前打开的 `.md` 文件；无法确定时询问用户
3. **读取文件**：读取最新的 MD 文件内容
4. **同步到 iWiki**：
   - 目标位置：个人空间 → 工作文件夹 (parentid: 4018520220)
   - 先用 `createDocument` 创建文档，再用 `saveDocument` 写入完整内容
   - 如已存在同名文档，更新而非重复创建
5. **转化为 Excel**：
   - 使用 `md-to-excel` MCP 工具，document 模式
   - 输出到 `g:\tianyishao\Moos-share\data\context\__created\work\to_excel\`
6. **完成报告**：输出结构化的执行结果报告

## 使用示例

```
/confirm_requirement                              → 确认当前打开的需求文档
/confirm_requirement ./我的需求文档.md              → 确认指定路径的需求文档
```

## 输出格式示例

```
✅ 需求文档已确认并发布

| 操作 | 状态 | 详情 |
|---|---|---|
| iWiki 同步 | ✅ | docid: XXXX，链接: https://iwiki.woa.com/pages/XXXX |
| Excel 转换 | ✅ | 输出: xxx.xlsx |
| 本地 MD | ✅ | 路径: xxx.md |
```
