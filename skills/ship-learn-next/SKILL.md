---
name: ship-learn-next
description: |
  将知识转化为实践的迭代学习助手。
  
  核心理念："100次重复胜过100小时学习"
  
  三阶段循环：
  - SHIP (交付): 创造真实存在的东西
  - LEARN (反思): 对发生的事情进行诚实反思
  - NEXT (迭代): 基于经验规划下一次迭代
  
  当用户提到：
  - "把XX转成实践计划"
  - "从笔记生成学习计划"
  - "设计一个学习迭代"
  - "如何把学到的用起来"
  时使用此 Skill。
triggers:
  - "实践计划"
  - "学习计划"
  - "迭代学习"
  - "ship-learn"
  - "知识转化"
  - "学以致用"
---

# Ship-Learn-Next 工作流

## 启动确认

在开始之前，确认：
- 知识来源主题（如 reading, product, ai 等）
- 学习目标或想要转化的知识点
- 期望的时间周期（可选，默认 4 周）

## Step 1: 知识提取 (KNOW)

从用户指定的 Context 主题中读取相关内容：
- 使用 `get_context(topic)` 获取完整内容
- 或使用 `query_context(query, topics)` 搜索特定知识点

**输出**: 知识摘要（关键概念、可实践建议、用户笔记）

## Step 2: 计划生成 (PLAN)

基于 Ship-Learn-Next 框架生成迭代计划：

### 计划结构
```
Ship-Learn-Next Plan - {任务名称}
├── 任务概述
│   ├── 学习目标
│   ├── 知识来源
│   └── 预期成果
├── 迭代计划 (4周)
│   ├── Week 1: SHIP → LEARN → NEXT
│   ├── Week 2: SHIP → LEARN → NEXT
│   ├── Week 3: SHIP → LEARN → NEXT
│   └── Week 4: SHIP → LEARN → NEXT
├── 进度跟踪表
└── 反思记录区
```

### 每个迭代包含
- **SHIP**: 具体交付物（代码、文档、原型、文章等）
- **LEARN**: 反思问题清单
  - 什么有效？
  - 什么无效？
  - 有什么意外发现？
  - 下次如何改进？
- **NEXT**: 基于反思的下一步行动

## Step 3: 执行跟踪 (TRACK)

用户完成一次迭代后：
- 记录 SHIP 交付物
- 引导完成 LEARN 反思
- 生成 NEXT 建议

使用 `track_iteration(plan_id, iteration, ship_result, learn_reflection)` 记录

## Step 4: 闭环反馈 (CLOSE)

将学习成果和反思写回日记：
- 使用 `add_note(topic="reflection", content=反思总结)`
- 可选择写回原始知识主题

## Step 5: 分享输出 (SHARE) - 可选

将学习历程导出为 PPT 分享：
- 使用 `export_plan_to_ppt(plan_id, style)`
- 调用 huashu-slides 生成演示文稿

## 可用 MCP 工具

| 工具 | 用途 |
|------|------|
| `get_context(topic)` | 读取知识库内容 |
| `query_context(query, topics)` | 搜索相关知识点 |
| `add_note(content, topic, title)` | 添加反思记录 |
| `create_ship_plan(topic, focus)` | 创建实践计划 |
| `track_iteration(plan_id, ...)` | 记录迭代进度 |
| `export_plan_to_ppt(plan_id, style)` | 导出 PPT |

## 输出规范

### 计划文档位置
`skills/ship-learn-next/plans/Plan-{任务名}-{日期}.md`

### 文档格式
- Markdown 格式
- 包含完整的 Ship-Learn-Next 结构
- 进度跟踪表格
- 反思记录区域

### 示例计划命名
- `Plan-Prompt工程-20260228.md`
- `Plan-产品冷启动-20260301.md`
