# Moos - 人机协作的知识操作系统

> **不是工具，而是搭档。**
> 
> 一套基于 Claude Code 的个人知识管理系统，让你和 AI 共同构建可持续运转的知识基础设施。

<p align="center">
  <img src="https://img.shields.io/badge/MCP-Protocol-blue" alt="MCP">
  <img src="https://img.shields.io/badge/Obsidian-Compatible-purple" alt="Obsidian">
  <img src="https://img.shields.io/badge/Ship--Learn--Next-Framework-green" alt="SLN">
</p>

---

## ✨ 核心亮点

### 1. 人机协作，而非人机交互

传统工具是「你提需求，它给结果」的主仆关系。Moos 是「共同建设」的搭档关系：

- 你提供思路和方向
- AI 理解意图 → 调用上下文 → 制定方案 → 推动执行
- 你们一起搭建一个可持续运转的基础设施

> "真正的杠杆不是单次使用 AI，而是和 AI 一起构建系统。"

### 2. 知识 → 实践 的完整闭环

内置 **Ship-Learn-Next** 实践框架：

```
SHIP (交付) → LEARN (反思) → NEXT (迭代)
     ↑                            ↓
     └──── 持续循环成长 ──────────┘
```

- **SHIP**: 每周必须有产出（产品分析、代码实现、文章输出）
- **LEARN**: 每周必须有反思（什么有效、什么无效、关键洞察）
- **NEXT**: 每周必须有改进（基于反思的调整）

### 3. Obsidian 原生兼容

输出的 Markdown 100% 兼容 Obsidian：

```yaml
---
created: "2026-03-02 14:30:00"
tags: ["ai/agent/claude", "collected"]
source-type: collected
source: articles
url: "https://example.com/article"
links: ["[[MCP]]", "[[RAG]]"]
---
```

- ✅ **Frontmatter** - 完整的元数据
- ✅ **层级标签** - `ai/agent/claude` 格式
- ✅ **双向链接** - `[[概念]]` 自动识别
- ✅ **图谱可视化** - Obsidian Graph View

### 4. 内容身份分离

知识管理中，**内容的来源决定了它的价值**：

| 类型 | 存放位置 | 特点 |
|------|----------|------|
| **原生内容** | `context/__created/` | 你的思考、创作、复盘 |
| **收集内容** | `context/__collected/` | 外部文章、笔记、资料 |
| **原始数据** | `raw/` | AI 生成、同步备份（Git 忽略）|

不再混淆「我的观点」和「他人的观点」。

### 5. 主题自动演进

传统工具的主题是静态配置。Moos 的主题是**动态生长**的：

1. **发现** - AI 分析内容，识别潜在新主题
2. **创建** - 自动创建主题，设置关键词
3. **演进** - 定期扩展关键词，更新描述
4. **合并** - 检测相似主题，建议合并

```bash
# AI 自动发现新主题
/manage_topic action=suggest_new

# 查看所有主题
/list_topics
```

### 6. MCP 原生集成

通过 **Model Context Protocol** 与 Claude Code 深度集成：

```json
{
  "mcpServers": {
    "personal-assistant": {
      "command": "python",
      "args": ["-m", "pa.mcp_server"]
    }
  }
}
```

无需额外界面，直接在对话中使用：

```
你: 收集这篇文章 https://example.com/ai-agent
AI: [调用 collect_content] 已收集，生成 Obsidian 格式，存储到 __collected/articles/ai/

你: 记录一下今天关于 Agent 的新想法
AI: [调用 add_note] 已记录到 raw/generated/work/

你: 创建 Ship-Learn-Next 计划，聚焦 Prompt Engineering
AI: [调用 create_ship_plan] 计划已创建，4 周迭代周期
```

---

## 🏗️ 架构设计

### 极简主义

- **无向量数据库** - 依赖 Claude Code 200K context 处理知识库
- **本地优先** - 所有数据存储于本地文件系统
- **Git 版本控制** - 每次变更可追溯，GitHub 私人仓库备份

### 目录结构

```
Moos/
├── 📁 data/
│   ├── 📁 context/              # Obsidian Vault（Git 备份）
│   │   ├── 📁 __created/        # 你的原创内容 ⭐
│   │   └── 📁 __collected/      # 收集的内容 📥
│   ├── 📁 docs/                 # 项目文档
│   └── 📁 raw/                  # 原始数据（Git 忽略）
│       └── 📁 generated/        # AI 生成的内容
│
├── 📁 src/pa/                   # 核心代码
│   ├── 📄 mcp_server.py         # MCP Server
│   ├── 📄 router/engine.py      # 路由引擎
│   └── 📁 topics/manager.py     # 主题管理器
│
├── 📁 skills/                   # Skill 扩展
│   └── 📁 ship-learn-next/      # 实践学习框架
│
└── 📁 .codebuddy/rules/         # 项目规则
    ├── 📄 data-file-management.md
    └── 📄 git-backup.md
```

---

## 🚀 快速开始

### 1. 安装

```bash
git clone https://github.com/suud003/knowledgeRes.git
cd knowledgeRes

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .
```

### 2. 配置

```bash
# 复制示例配置
cp config.example.yaml config.yaml

# 编辑 config.yaml，添加飞书凭证（可选）
```

### 3. 启动 MCP Server

在 Claude Code 配置中添加（**关键：必须设置正确的 cwd 参数**）：

```json
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

**重要提示：**
- `cwd` 必须设置为项目的绝对路径
- Windows路径需要使用双反斜杠 `\\` 转义
- 如果遇到权限错误，请参考 `MCP_CONFIG_GUIDE.md` 进行故障排除

### 4. 验证安装

重启 Claude Code 后，可以通过以下命令验证 MCP 服务器是否正常工作：

```bash
# 在 Claude Code 中测试
list_topics()  # 应该返回主题列表
add_note(content="测试笔记", topic="test")  # 应该成功添加笔记
```

如果遇到问题，请检查：
1. 依赖是否安装：`pip install -e .`
2. cwd路径是否正确
3. 项目目录是否有读写权限

### 4. 使用

重启 Claude Code，开始使用：

```
你: 收集 https://mp.weixin.qq.com/s/xxx 这篇文章
AI: 已抓取页面，提取正文，生成摘要，存储到 __collected/articles/ideas/

你: 帮我创建一个关于 AI Agent 的实践计划
AI: 已创建 Ship-Learn-Next 计划，4 周周期，第一周聚焦...
```

---

## 📊 数据流

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   数据源     │────▶│  AI 处理器   │────▶│  知识库      │
│             │     │             │     │             │
│ • 飞书      │     │ • 内容理解   │     │ • Obsidian  │
│ • Flomo     │     │ • 主题分类   │     │ • 双链接     │
│ • 网页      │     │ • 格式转换   │     │ • 图谱       │
│ • 微信文章  │     │ • 摘要生成   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   实践应用   │
                                        │             │
                                        │ • Ship-Learn│
                                        │ • 写作素材  │
                                        │ • 复盘反思  │
                                        └─────────────┘
```

---

## 🎯 适用场景

| 场景 | 如何使用 | 收益 |
|------|----------|------|
| **知识工作者** | 收集文章 → AI 整理 → Obsidian 深度阅读 | 读得少但用得深 |
| **产品经理** | Ship-Learn-Next 实践 → 每周产品分析 | 从消费者到建设者 |
| **开发者** | MCP 扩展开发 → 自动化工作流 | 构建个人工具链 |
| **终身学习者** | 多源数据汇聚 → 主题自动演进 | 知识网络自生长 |

---

## 🛠️ 扩展开发

### 添加新数据源

```python
from pa.collectors.base import BaseCollector

class MyCollector(BaseCollector):
    async def collect(self):
        # 你的采集逻辑
        return records
```

### 添加新 Skill

```python
# skills/my-skill/SKILL.md
# skills/my-skill/scripts/
# skills/my-skill/templates/
```

---

## 📚 相关资源

- **Obsidian**: https://obsidian.md
- **MCP 协议**: https://modelcontextprotocol.io
- **Claude Code**: https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview

---

## 🤝 协作哲学

> "大多数人使用 AI 的方式是「消费」——让 AI 生成内容。
> 我们做的是「建设」——和 AI 一起搭建一个可持续运转的基础设施。"

Moos 不是一款「软件」，而是一种「工作方式」：
- 你和 AI 共同定义问题
- AI 理解上下文并执行
- 你们一起迭代优化系统

---

## 📝 License

MIT © tianyishao

---

<p align="center">
  Built with ❤️ by Human + AI
</p>
