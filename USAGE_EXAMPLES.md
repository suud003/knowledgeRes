# Moos MCP 工具使用示例大全

## 📚 基础操作示例

### 1. 查看系统状态

```python
# 查看所有可用主题
list_topics()

# 预期输出：
# ['personal', 'writing', 'tasks', 'preferences', 'reflection', 'product', 'work', 'reading', 'ideas', 'ai']
```

### 2. 添加个人笔记

#### 工作记录
```python
# 记录工作进展
add_note(
    content="今天完成了产品需求文档的初稿，重点优化了用户流程部分。明天需要与设计团队对齐交互细节。",
    topic="work"
)

# 记录会议要点
add_note(
    content="周会要点：1. 下季度重点聚焦用户增长 2. 需要加强数据埋点 3. 团队需要提升技术文档质量",
    topic="work"
)
```

#### 学习笔记
```python
# 记录技术学习心得
add_note(
    content="今天学习了MCP协议的工作原理，发现它可以实现AI与本地工具的深度集成。下一步想尝试开发自定义MCP工具。",
    topic="ai"
)

# 记录读书笔记
add_note(
    content="《设计心理学》第3章：好的设计应该让用户感到掌控感。这让我想到我们产品的导航可以更直观一些。",
    topic="reading"
)
```

#### 生活记录
```python
# 记录个人反思
add_note(
    content="今天发现工作效率最高的时段是上午9-11点，应该把重要任务安排在这个时间段。",
    topic="reflection"
)

# 记录灵感想法
add_note(
    content="突然想到：如果能将AI知识库与日常写作工具集成，可以大大提升内容创作效率。",
    topic="ideas"
)
```

### 3. 批量添加笔记

```python
# 批量记录一周的工作总结
weekly_notes = [
    {
        "content": "周一：完成了产品需求文档初稿，与团队对齐了技术方案",
        "topic": "work"
    },
    {
        "content": "周二：参加了技术分享会，学习了新的前端框架",
        "topic": "work"
    },
    {
        "content": "周三：发现了一个提高代码质量的工具，明天可以试用",
        "topic": "product"
    },
    {
        "content": "周四：用户反馈显示登录流程需要优化，需要重新设计",
        "topic": "product"
    },
    {
        "content": "周五：本周总结：完成了主要任务，但文档质量需要提升",
        "topic": "reflection"
    }
]

for note in weekly_notes:
    add_note(content=note["content"], topic=note["topic"])
```

## 🌐 内容收集示例

### 1. 收集技术文章

```python
# 收集AI相关文章
collect_content(
    url="https://example.com/ai-agent-development",
    html="""
    <html>
    <head>
        <title>AI Agent开发指南</title>
        <meta name="author" content="技术专家">
    </head>
    <body>
        <h1>AI Agent开发指南</h1>
        <p>本文介绍了如何构建智能AI Agent...</p>
    </body>
    </html>
    """,
    topic="ai"
)
```

### 2. 收集产品分析

```python
# 收集产品分析文章
collect_content(
    url="https://example.com/product-analysis",
    html="""
    <html>
    <head>
        <title>优秀产品的设计原则</title>
    </head>
    <body>
        <h1>优秀产品的设计原则</h1>
        <p>1. 用户为中心 2. 简洁易用 3. 持续迭代...</p>
    </body>
    </html>
    """,
    topic="product"
)
```

### 3. 批量收集内容

```python
# 批量收集多篇文章
articles = [
    {
        "url": "https://example.com/article1",
        "html": "<html><title>文章1</title><body>内容1</body></html>",
        "topic": "ai"
    },
    {
        "url": "https://example.com/article2", 
        "html": "<html><title>文章2</title><body>内容2</body></html>",
        "topic": "product"
    },
    {
        "url": "https://example.com/article3",
        "html": "<html><title>文章3</title><body>内容3</body></html>",
        "topic": "reading"
    }
]

for article in articles:
    collect_content(
        url=article["url"],
        html=article["html"],
        topic=article["topic"]
    )
```

## 📊 知识查询和管理

### 1. 搜索知识库

```python
# 搜索AI相关内容
query_context(query="AI Agent开发")

# 搜索工作相关记录
query_context(query="本周工作进展")

# 搜索产品设计思考
query_context(query="用户体验优化")
```

### 2. 主题管理

```python
# 查看主题详情
manage_topic(action="list")

# 创建新主题（如果需要）
# 注意：通常通过编辑config.yaml来添加新主题
```

## 🚀 学习计划管理

### 1. 创建学习计划

```python
# 创建AI学习计划
create_ship_plan(
    topic="ai",
    focus="掌握MCP协议和AI Agent开发",
    duration_weeks=4
)

# 创建产品学习计划
create_ship_plan(
    topic="product", 
    focus="提升产品设计和用户研究能力",
    duration_weeks=6
)
```

### 2. 记录学习进度

```python
# 记录第一周学习成果
track_iteration(
    plan_id="ai",
    week=1,
    ship_result="完成了MCP服务器的配置和测试，理解了基本工作原理",
    learn_reflection="发现配置cwd参数是关键，需要确保路径正确。MCP协议比想象中强大。",
    next_adjustment="下周重点学习如何开发自定义MCP工具"
)

# 记录第二周学习成果
track_iteration(
    plan_id="ai", 
    week=2,
    ship_result="开发了一个简单的MCP工具，实现了自定义功能",
    learn_reflection="MCP工具开发需要熟悉FastMCP框架，参数传递需要特别注意类型匹配",
    next_adjustment="下周尝试集成更多数据源，完善工具功能"
)
```

### 3. 查看学习计划

```python
# 列出所有学习计划
list_ship_plans()
```

## 🎯 实际工作场景示例

### 场景1：产品需求分析

```python
# 收集竞品分析文章
collect_content(url="竞品文章链接", html="内容", topic="product")

# 记录用户反馈
add_note(
    content="用户反馈：希望增加导出功能，当前的数据分析不够直观",
    topic="product"
)

# 记录产品决策
add_note(
    content="产品决策：下个版本优先开发数据导出功能，预计需要2周开发时间",
    topic="work"
)
```

### 场景2：技术方案设计

```python
# 收集技术方案参考
collect_content(url="技术方案文章", html="内容", topic="ai")

# 记录技术思考
add_note(
    content="技术方案：使用MCP协议实现AI与本地工具的集成，可以避免API调用限制",
    topic="ai"
)

# 记录实现细节
add_note(
    content="实现细节：需要处理文件路径权限问题，确保MCP服务器有正确的读写权限",
    topic="work"
)
```

### 场景3：个人成长规划

```python
# 创建年度学习计划
create_ship_plan(
    topic="personal-growth",
    focus="提升技术能力和产品思维",
    duration_weeks=52
)

# 季度复盘
track_iteration(
    plan_id="personal-growth",
    week=13,
    ship_result="完成了3个技术项目，阅读了5本专业书籍",
    learn_reflection="发现系统化学习比碎片化学习更有效，需要建立更清晰的学习路径",
    next_adjustment="下季度重点提升产品设计能力，计划参加相关培训"
)
```

## 🔧 高级功能示例

### 1. 自定义主题分类

如果需要添加新的主题分类，编辑 `config.yaml`：

```yaml
context:
  core_topics:
    # 现有主题...
    
    # 添加新主题
    programming:
      name: "编程技术"
      description: "编程语言、框架、工具等相关内容"
      keywords: ["Python", "JavaScript", "React", "算法", "数据结构"]
    
    business:
      name: "商业思维" 
      description: "商业模式、市场分析、商业决策"
      keywords: ["商业模式", "市场分析", "商业决策", "创业"]
```

### 2. 集成外部数据源

```python
# 集成飞书数据（需要配置飞书API）
# 飞书同步功能会自动将多维表格数据导入知识库
```

### 3. 自动化工作流

```python
# 可以结合其他工具创建自动化工作流
# 例如：定时收集特定网站内容，自动分类存储
```

## 🛠️ 故障排除示例

### 问题：MCP工具调用失败

```python
# 错误示例：缺少cwd配置
# 解决方案：确保Claude Code配置中包含正确的cwd路径

# 正确配置示例：
{
  "mcpServers": {
    "personal-assistant": {
      "command": "python",
      "args": ["-m", "pa.mcp_server"],
      "cwd": "g:\\tianyishao\\Moos-share"
    }
  }
}
```

### 问题：内容分类不准确

```python
# 解决方案：调整config.yaml中的关键词
# 或者手动指定topic参数

# 手动指定主题
add_note(content="内容", topic="明确的主题名称")
collect_content(url="链接", html="内容", topic="明确的主题名称")
```

## 💡 最佳实践建议

1. **及时记录**：想到就记，避免遗忘
2. **分类明确**：使用合适的主题分类
3. **内容完整**：确保记录包含足够上下文
4. **定期复盘**：每周回顾知识积累情况
5. **持续优化**：根据使用体验调整分类策略

---

**开始使用**：复制上面的示例代码，在Claude Code中执行，立即体验Moos的强大功能！

> 提示：可以先从简单的 `add_note()` 和 `list_topics()` 开始，逐步尝试更复杂的功能。