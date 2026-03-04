# /sync

## 功能
触发数据同步，将所有数据源的内容同步整理到 Context 文件夹

## 参数
无

## 执行步骤

1. **执行同步**：调用 `sync_data` MCP 工具
2. **展示结果**：展示同步处理的数据条数和写入的文件列表

## 输出格式示例

```
🔄 数据同步完成！

处理数据：15 条
写入文件：
  ✅ context/ai/ai_context.md（8 条更新）
  ✅ context/reading/reading_context.md（4 条更新）
  ✅ context/work/work_context.md（3 条更新）
```
