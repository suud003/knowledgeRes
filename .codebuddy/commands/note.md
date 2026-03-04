# /note <内容> [topic]

## 功能
快速添加一条笔记到知识库

## 参数
- `内容`（必填）：笔记内容
- `topic`（可选）：指定主题，可选值：personal / writing / tasks / preferences / reflection / product / work / reading / ideas / ai。不指定则根据内容自动判断最合适的主题

## 执行步骤

1. **判断主题**：如果用户未指定 topic，根据内容关键词自动推断最合适的主题
2. **添加笔记**：调用 `add_note` MCP 工具，传入 content 和 topic
3. **确认保存**：向用户展示保存结果

## 输出格式示例

```
📝 已记录到 [AI 相关]：
"你的笔记内容预览..."
```
