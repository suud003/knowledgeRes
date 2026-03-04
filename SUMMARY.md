# Moos 项目总结

## 🎯 核心价值

**Moos 是一个「人机协作的知识操作系统」**，让你和AI共同构建可持续运转的知识基础设施。

### 核心理念
- **不是工具，而是搭档**：你和AI共同定义问题、制定方案、推动执行
- **知识→实践闭环**：内置Ship-Learn-Next实践框架
- **本地优先**：所有数据存储于本地，完全由你掌控
- **Obsidian兼容**：100%兼容Obsidian，支持双向链接和知识图谱

## 📁 项目结构

```
Moos-share/
├── 📁 data/                    # 数据目录
│   ├── 📁 context/             # 知识库（Obsidian格式，Git备份）
│   │   ├── 📁 __created/       # 你的原创内容
│   │   └── 📁 __collected/     # 收集的内容
│   └── 📁 raw/                 # 原始数据（Git忽略）
├── 📁 src/pa/                  # 核心代码
│   └── 📄 mcp_server.py       # MCP服务器入口
├── 📁 skills/                  # Skill扩展
├── 📄 config.yaml              # 配置文件
└── 📄 README.md                # 详细文档
```

## 🚀 快速开始

### 1. 验证MCP配置

在Claude Code中执行：

```python
list_topics()  # 应该返回主题列表
```

### 2. 第一天行动计划（30分钟）

1. **验证连接**：`list_topics()`
2. **添加笔记**：`add_note(content="第一条笔记", topic="work")`
3. **收集内容**：`collect_content(url="示例链接", html="内容", topic="ai")`
4. **创建计划**：`create_ship_plan(topic="moos", focus="掌握使用方法", duration_weeks=2)`

## 🔧 核心MCP工具

### 基础工具

| 工具 | 功能 | 示例 |
|------|------|------|
| `list_topics()` | 查看所有主题 | `list_topics()` |
| `add_note()` | 添加个人笔记 | `add_note(content="笔记", topic="主题")` |
| `collect_content()` | 收集网页内容 | `collect_content(url="链接", html="内容", topic="主题")` |
| `query_context()` | 搜索知识库 | `query_context(query="搜索词")` |

### 高级工具

| 工具 | 功能 | 示例 |
|------|------|------|
| `create_ship_plan()` | 创建学习计划 | `create_ship_plan(topic="主题", focus="重点", duration_weeks=4)` |
| `track_iteration()` | 记录学习进度 | `track_iteration(plan_id="计划", week=1, ship_result="成果", learn_reflection="反思")` |
| `manage_topic()` | 管理主题分类 | `manage_topic(action="list")` |

## 📊 使用场景示例

### 日常知识管理

```python
# 早晨：快速收集
collect_content(url="技术文章", html="内容", topic="ai")

# 工作中：记录想法
add_note(content="会议要点：下季度重点...", topic="work")

# 晚上：复盘总结
add_note(content="今日反思：效率最高的时段是...", topic="reflection")
```

### 学习成长

```python
# 创建学习计划
create_ship_plan(topic="ai", focus="掌握MCP开发", duration_weeks=4)

# 每周记录进度
track_iteration(
    plan_id="ai",
    week=1,
    ship_result="完成MCP配置",
    learn_reflection="发现cwd配置是关键"
)
```

## 🛠️ 配置要点

### MCP服务器配置

在Claude Code中添加：

```json
{
  "mcpServers": {
    "personal-assistant": {
      "command": "python",
      "args": ["-m", "pa.mcp_server"],
      "cwd": "g:\\tianyishao\\Moos-share"  // 关键：绝对路径
    }
  }
}
```

### 主题配置

编辑 `config.yaml` 自定义主题：

```yaml
context:
  core_topics:
    my_topic:
      name: "我的主题"
      description: "主题描述"
      keywords: ["关键词1", "关键词2"]
```

## 🆘 常见问题

### 问题1：MCP工具调用失败

**症状**：`list_topics()` 返回错误

**解决**：
1. 检查cwd路径是否正确
2. 确认项目目录有读写权限
3. 重启Claude Code

### 问题2：内容分类不准确

**症状**：收集的内容被分到错误主题

**解决**：
1. 调整config.yaml中的关键词
2. 手动指定topic参数
3. 训练AI理解你的分类偏好

## 📚 详细文档

| 文档 | 内容 | 用途 |
|------|------|------|
| [README.md](README.md) | 完整项目介绍 | 了解项目理念和架构 |
| [PERSONAL_KNOWLEDGE_GUIDE.md](PERSONAL_KNOWLEDGE_GUIDE.md) | 知识库构建指南 | 系统学习使用方法 |
| [QUICK_START.md](QUICK_START.md) | 快速入门指南 | 第一天行动计划 |
| [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) | 使用示例大全 | 具体操作参考 |
| [MCP_CONFIG_GUIDE.md](MCP_CONFIG_GUIDE.md) | MCP配置指南 | 故障排除和配置 |

## 🎯 成功指标

### 短期目标（1个月）
- ✅ 建立每日记录习惯
- ✅ 积累50+条知识记录
- ✅ 掌握核心MCP工具

### 中期目标（3个月）
- ✅ 知识库内容达到500+条
- ✅ 形成个人知识体系
- ✅ 实现知识自动化管理

### 长期目标（6个月+）
- ✅ 知识库成为核心竞争力
- ✅ 建立个人品牌影响力
- ✅ 实现知识价值最大化

## 💡 最佳实践

1. **质量优于数量**：每条记录都要有价值
2. **及时记录**：想到就记，避免遗忘
3. **建立连接**：主动关联相关知识
4. **持续迭代**：根据反馈不断优化
5. **享受过程**：知识管理是长期投资

## 🔮 未来扩展

随着使用深入，可以：
- 开发自定义MCP工具
- 集成更多数据源
- 建立自动化工作流
- 开发知识分析仪表板

---

**立即开始**：执行 `list_topics()` 验证配置，然后开始你的知识管理之旅！

> 记住：最好的开始时间是现在。开始行动吧！🚀