# Yogurt - 人机协作的知识操作系统

> **不是工具，而是搭档。**
> 
> 一套基于 MCP 协议的个人知识管理系统，内置丰富的自定义指令和 Skill 扩展，支持 **CodeBuddy** / **Cursor** 等 AI IDE，让你和 AI 共同构建可持续运转的知识基础设施。
>
> 只需一句 `/collect`、`/note`、`/plan`，AI 就能理解你的意图并自动执行。

<p align="center">
  <img src="https://img.shields.io/badge/MCP-Protocol-blue" alt="MCP">
  <img src="https://img.shields.io/badge/CodeBuddy-Supported-orange" alt="CodeBuddy">
  <img src="https://img.shields.io/badge/Cursor-Supported-yellow" alt="Cursor">
  <img src="https://img.shields.io/badge/Ship--Learn--Next-Framework-green" alt="SLN">
</p>

---

## ✨ 核心亮点

### 1. 人机协作，而非人机交互

传统工具是「你提需求，它给结果」的主仆关系。Yogurt 是「共同建设」的搭档关系：

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

### 3. 内容身份分离

知识管理中，**内容的来源决定了它的价值**：

| 类型 | 存放位置 | 特点 |
|------|----------|------|
| **原生内容** | `context/__created/` | 你的思考、创作、复盘 |
| **收集内容** | `context/__collected/` | 外部文章、笔记、资料 |
| **原始数据** | `raw/` | AI 生成、同步备份 |

不再混淆「我的观点」和「他人的观点」。

### 4. 自定义指令系统

内置 **11 个即用型自定义指令**，覆盖知识管理全流程：

| 指令 | 功能 | 说明 |
|------|------|------|
| `/collect` | 收集文章 | 抓取网页/文章，生成 Markdown 格式存储 |
| `/note` | 快速笔记 | 随手记录想法，自动归类到主题 |
| `/save` | 保存内容 | 将对话中的内容保存为知识文件 |
| `/digest` | 内容摘要 | 对长文/多篇文章生成结构化摘要 |
| `/news` | 资讯追踪 | 获取 RSS 订阅的最新资讯 |
| `/search` | 知识搜索 | 在知识库中搜索已有内容 |
| `/topics` | 主题管理 | 查看/管理所有知识主题 |
| `/plan` | 创建计划 | 创建 Ship-Learn-Next 实践计划 |
| `/track` | 追踪进度 | 追踪 SLN 计划执行情况 |
| `/recent` | 最近动态 | 查看近期知识库变更 |
| `/sync` | 同步数据 | 同步外部数据源 |

> 💡 所有指令均可在 AI 对话中直接使用，也可通过 `.codebuddy/commands/` 目录自行扩展。

### 5. 主题自动演进

传统工具的主题是静态配置。Yogurt 的主题是**动态生长**的：

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

通过 **Model Context Protocol** 与 **CodeBuddy** / **Cursor** 深度集成：

- **CodeBuddy**：在项目根目录 `.codebuddy/mcp.json` 中配置
- **Cursor**：在项目根目录 `.cursor/mcp.json` 中配置

无需额外界面，直接在 AI 对话中使用：

```
你: 收集这篇文章 https://example.com/ai-agent
AI: [调用 collect_content] 已收集，生成 Markdown 格式，存储到 __collected/articles/ai/

你: 记录一下今天关于 Agent 的新想法
AI: [调用 add_note] 已记录到 raw/generated/work/

你: 创建 Ship-Learn-Next 计划，聚焦 Prompt Engineering
AI: [调用 create_ship_plan] 计划已创建，4 周迭代周期
```

---

## 🏗️ 架构设计

### 极简主义

- **无向量数据库** - 依赖 AI IDE 的大上下文窗口处理知识库
- **本地优先** - 所有数据存储于本地文件系统
- **Git 版本控制** - 每次变更可追溯，GitHub 私人仓库备份

### 目录结构

```
Moos/
├── 📁 data/
│   ├── 📁 context/              # 知识库（Git 备份）
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
│   ├── 📁 ship-learn-next/      # 实践学习框架
│   └── 📁 huashu-slides/        # 华书幻灯片生成
│
├── 📁 .codebuddy/               # CodeBuddy 配置
│   ├── 📁 commands/             # 自定义指令（11 个）
│   ├── 📁 rules/                # 项目规则
│   └── 📄 mcp.json              # MCP 服务器配置
│
└── 📁 .cursor/                  # Cursor 配置（可选）
    └── 📄 mcp.json              # MCP 服务器配置
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

### 2. 配置 MCP Server

#### CodeBuddy（推荐）

在项目根目录创建 `.codebuddy/mcp.json`：

```json
{
  "mcpServers": {
    "personal-assistant": {
      "command": "python",
      "args": ["-m", "pa.mcp_server"],
      "cwd": "<项目绝对路径>"
    }
  }
}
```

> 💡 将 `<项目绝对路径>` 替换为你的实际路径，如 `g:\tianyishao\Moos-share`

**重要提示：**
- `cwd` 必须设置为项目的绝对路径
- Windows 路径需要使用双反斜杠 `\\` 转义

### 3. 验证安装

重启 IDE 后，在 AI 对话中测试 MCP 服务器是否正常工作：

```
你: 列出所有主题
AI: [调用 list_topics] 返回主题列表...

你: 添加一条测试笔记
AI: [调用 add_note] 已成功添加笔记
```

如果遇到问题，请检查：
1. 依赖是否安装：`pip install -e .`
2. `cwd` 路径是否正确
3. 项目目录是否有读写权限

### 4. 开始使用

在 AI 对话中直接使用：

```
你: 收集 https://mp.weixin.qq.com/s/xxx 这篇文章
AI: 已抓取页面，提取正文，生成 Markdown 格式，存储到 __collected/articles/ideas/

你: 帮我创建一个关于 AI Agent 的实践计划
AI: 已创建 Ship-Learn-Next 计划，4 周周期，第一周聚焦...
```

---

## 📊 数据流

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   数据源     │────▶│  AI 处理器   │────▶│  知识库      │
│             │     │             │     │             │
│ • Flomo     │     │ • 内容理解   │     │ • Markdown  │
│ • 网页      │     │ • 主题分类   │     │ • 双链接     │
│ • 微信文章  │     │ • 格式转换   │     │ • 图谱       │
│             │     │ • 摘要生成   │     │             │
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
| **知识工作者** | 收集文章 → AI 整理 → 深度阅读 | 读得少但用得深 |
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

- **MCP 协议**: https://modelcontextprotocol.io
- **CodeBuddy**: https://codebuddy.ai
- **Cursor**: https://cursor.com

---

## 🤝 协作哲学

> "大多数人使用 AI 的方式是「消费」——让 AI 生成内容。
> 我们做的是「建设」——和 AI 一起搭建一个可持续运转的基础设施。"

Yogurt 不是一款「软件」，而是一种「工作方式」：
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
