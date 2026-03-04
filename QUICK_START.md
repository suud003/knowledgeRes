# Moos 快速入门指南

## 🚀 第一天行动计划（30分钟）

### 步骤1：验证MCP连接（2分钟）

在Claude Code中执行：

```python
# 测试MCP服务器是否正常工作
list_topics()
```

**期望结果**：返回主题列表，如：
```
['personal', 'writing', 'tasks', 'preferences', 'reflection', 'product', 'work', 'reading', 'ideas', 'ai']
```

### 步骤2：添加第一条笔记（3分钟）

```python
# 记录今天的工作反思
add_note(
    content="今天成功配置了Moos的MCP服务器，开始构建个人知识库。感觉这个系统很有潜力，可以帮我更好地管理知识。",
    topic="work"
)
```

**期望结果**：返回成功消息，如：
```
笔记已成功添加到主题 'work'
```

### 步骤3：收集第一篇文章（5分钟）

```python
# 收集一篇关于AI的文章（使用示例URL）
collect_content(
    url="https://example.com/ai-knowledge-management",
    html="<html><head><title>AI知识管理的最佳实践</title></head><body><p>这篇文章介绍了如何利用AI构建个人知识库...</p></body></html>",
    topic="ai"
)
```

**期望结果**：返回收集成功消息，文件保存到 `data/context/__collected/articles/ai/`

### 步骤4：创建第一个学习计划（5分钟）

```python
# 创建一个关于Moos使用的学习计划
create_ship_plan(
    topic="moos",
    focus="掌握Moos知识库的使用方法",
    duration_weeks=2
)
```

**期望结果**：返回计划创建成功消息

## 📝 日常使用模式

### 早晨（5分钟）

**快速收集**：
```python
# 收集昨晚看到的好文章
collect_content(url="文章链接", html="内容", topic="相关主题")
```

### 工作中（随时）

**记录想法**：
```python
# 会议记录
add_note(content="今天会议决定：1. 产品功能优先级调整 2. 下周发布计划", topic="work")

# 技术心得
add_note(content="发现Claude Code的MCP功能比想象中强大，可以深度集成工作流", topic="ai")
```

### 晚上（10分钟）

**复盘总结**：
```python
# 工作复盘
add_note(content="今天完成了Moos配置，感觉知识管理效率会有很大提升。明天重点测试批量收集功能。", topic="reflection")

# 学习记录
track_iteration(
    plan_id="moos",
    week=1,
    ship_result="成功配置MCP服务器并添加了第一条笔记",
    learn_reflection="发现配置cwd参数是关键，相对路径容易导致权限错误",
    next_adjustment="明天尝试批量内容收集功能"
)
```

## 🔧 常用命令速查

### 基础操作

```python
# 查看所有主题
list_topics()

# 添加笔记
add_note(content="内容", topic="主题")

# 收集网页内容
collect_content(url="链接", html="HTML内容", topic="主题")

# 查询知识库
query_context(query="搜索关键词")
```

### 高级功能

```python
# 创建学习计划
create_ship_plan(topic="主题", focus="重点", duration_weeks=周数)

# 记录学习进度
track_iteration(plan_id="计划ID", week=周次, ship_result="交付成果", learn_reflection="学习反思")

# 管理主题
manage_topic(action="list")  # 列出主题
manage_topic(action="create", topic_key="新主题", name="显示名称")  # 创建新主题
```

## 🎯 第一周目标

### 完成以下里程碑：

- ✅ **Day 1**：成功添加第一条笔记和收集第一篇文章
- ✅ **Day 2**：建立每日记录习惯，添加3条以上笔记
- ✅ **Day 3**：尝试批量操作，收集5篇相关文章
- ✅ **Day 4**：创建第一个学习计划并记录进度
- ✅ **Day 5**：使用query_context搜索知识库内容
- ✅ **Day 6**：复盘一周使用体验，调整分类策略
- ✅ **Day 7**：建立稳定的知识管理流程

### 预期成果：

- 积累50+条有价值的知识记录
- 形成个人知识库的基本框架
- 掌握核心MCP工具的使用方法
- 建立可持续的知识管理习惯

## 🆘 常见问题解决

### 问题1：MCP工具调用失败

**症状**：`list_topics()` 返回错误或超时

**解决方案**：
1. 检查Claude Code的MCP配置
2. 确认 `cwd` 设置为绝对路径：`g:\\tianyishao\\Moos-share`
3. 重启Claude Code
4. 检查项目目录权限

### 问题2：内容分类不准确

**症状**：收集的内容被分到错误的主题

**解决方案**：
1. 查看config.yaml中的关键词配置
2. 手动调整分类，训练AI理解你的偏好
3. 创建更具体的主题分类

### 问题3：存储空间不足

**症状**：文件保存失败或系统变慢

**解决方案**：
1. 定期清理 `data/raw/generated/` 目录
2. 使用Git进行版本控制，删除历史大文件
3. 考虑使用外部存储

## 💡 小贴士

1. **从简单开始**：先建立记录习惯，再追求完美分类
2. **及时记录**：想到就记，避免遗忘
3. **质量优先**：每条记录都要有实际价值
4. **持续迭代**：根据使用反馈不断优化流程
5. **享受过程**：知识管理是长期投资，不要急于求成

---

**立即开始**：执行上面的"第一天行动计划"，30分钟后你就能体验到Moos的强大功能！

> 记住：最好的开始时间是现在，其次是明天。开始行动吧！🚀