# /plan [topic] [focus]

## 功能
创建一个 Ship-Learn-Next 实践学习计划，将知识转化为行动

## 参数
- `topic`（可选）：知识来源主题，如 ai、reading、product 等。不指定则询问
- `focus`（可选）：聚焦的具体知识点或方向，如 "Prompt 工程"、"游戏 AI 设计"

## 执行步骤

1. **确认参数**：如果用户未指定 topic 或 focus，询问具体学习方向
2. **创建计划**：调用 `create_ship_plan` MCP 工具
3. **展示计划**：向用户展示生成的计划概览

## 输出格式示例

```
📋 学习计划已创建！

🎯 主题：AI Agent 开发实践
📅 周期：4 周
📄 文件：plans/Plan-xxx.md

Week 1: SHIP → 完成 xxx
Week 2: SHIP → 完成 xxx
Week 3: SHIP → 完成 xxx
Week 4: SHIP → 完成 xxx

使用 /track 记录每周执行结果
```
