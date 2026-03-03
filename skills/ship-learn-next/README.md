# Ship-Learn-Next Skill

将知识转化为实践的迭代学习助手。

## 核心理念

> "100次重复胜过100小时学习"

**Ship-Learn-Next** 三阶段循环：
- **SHIP (交付)**: 创造真实存在的东西（代码、文档、原型、文章）
- **LEARN (反思)**: 对发生的事情进行诚实反思
- **NEXT (迭代)**: 基于经验规划下一次迭代

## 使用场景

当你遇到以下情况时，使用这个 Skill：
- 学了新知识，不知道如何使用
- 陷入「教程地狱」，学了很多但没产出
- 想把读书笔记、学习笔记转化为行动计划
- 需要一个结构化的学习方法

## 使用方法

### 1. 创建实践计划

```python
# 通过 MCP 工具调用
create_ship_plan(
    topic="reading",           # 知识来源主题
    focus="Prompt Engineering", # 关注的知识点（可选）
    duration_weeks=4           # 计划周期（默认4周）
)
```

示例对话：
```
你: 帮我把最近读的书转成实践计划
AI: 好的，我从你的 reading 主题中找到了关于 "Prompt Engineering" 的笔记。
    让我为你生成一个 4 周的 Ship-Learn-Next 计划...
```

### 2. 跟踪迭代进度

```python
track_iteration(
    plan_id="Plan-Prompt工程-20260228",
    week=1,
    ship_result="完成了3个工作场景的Prompt优化",
    learn_reflection="发现简洁的指令效果更好..."
)
```

### 3. 导出分享 PPT

```python
export_plan_to_ppt(
    plan_id="Plan-Prompt工程-20260228",
    style="snoopy"  # 可选风格
)
```

## 计划文档结构

生成的计划文档位于 `plans/Plan-{名称}-{日期}.md`：

```markdown
# Ship-Learn-Next Plan - Prompt工程实践

## 任务概述
- 学习目标
- 知识来源摘要
- 预期成果

## 迭代计划
### Week 1: 第一轮迭代
#### SHIP (交付)
用学到的 AI 技巧完成 1 个实际工作场景的优化

#### LEARN (反思)
1. 什么有效？
2. 什么无效？
3. 有什么意外发现？
4. 下次如何改进？

#### NEXT (迭代)
基于反思，优化下一轮执行方案

## 进度跟踪
| 周次 | 状态 | 交付物 | 完成日期 |

## 详细记录
### Week 1 执行记录
...
```

## 目录结构

```
skills/ship-learn-next/
├── README.md              # 本文件
├── SKILL.md               # Skill 定义（供 Claude 使用）
├── templates/
│   └── plan-template.md   # 计划文档模板
├── scripts/
│   ├── planner.py         # 计划生成器
│   ├── tracker.py         # 进度跟踪器
│   └── exporter.py        # PPT 导出器
├── plans/                 # 生成的计划文档（自动创建）
│   ├── Plan-XXX-20260228.md
│   └── ...
└── examples/
    └── sample-plan.md     # 示例计划
```

## 与 Personal Assistant 集成

这个 Skill 与 personal-assistant MCP 深度集成：

- **读取知识**: 通过 `get_context()` 和 `query_context()` 读取 Context
- **记录反思**: 通过 `add_note()` 将学习成果写回日记
- **PPT 导出**: 复用 huashu-slides Skill 的导出能力

## 自动化检测

系统会自动根据计划名称推断任务类型：

| 关键词 | 任务类型 | 示例交付物 |
|--------|----------|-----------|
| prompt, ai, gpt | AI 学习 | Prompt 模板库、优化案例 |
| 产品, PRD, 原型 | 产品设计 | 原型、用户访谈记录、PRD |
| 代码, 编程 | 编程开发 | 代码仓库、测试、文档 |
| 写作, 文章 | 内容创作 | 文章、博客、公众号 |
| 读书, 学习 | 课程学习 | 笔记、知识地图、行动清单 |

## 提示

1. **从简单开始**: 第一周的任务要小，确保能完成
2. **诚实反思**: LEARN 阶段要诚实，不管成功还是失败
3. **持续迭代**: NEXT 的建议要在下一轮执行
4. **记录一切**: 详细的记录是改进的基础
