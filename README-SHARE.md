# Personal Assistant - 个人知识中枢系统

> 用 3 天时间，和 AI 一起搭建你的「第二大脑」

这是个人知识中枢系统的可分享版本，**已移除所有敏感信息**。

---

## 它能做什么？

### 核心能力

| 能力 | 说明 | 示例 |
|------|------|------|
| **网页内容收集** | 自动提取文章正文、标题、作者 | 看到好文章，一键保存到知识库 |
| **知识库查询** | 用自然语言搜索你的笔记 | "我之前写的关于 AI 的思考" |
| **智能分类** | 自动将内容归类到不同主题 | 产品思考、工作记录、阅读笔记 |
| **飞书同步** | 同步飞书多维表格数据 | 日记、读书笔记自动导入 |

### 适用场景

- 收藏了很多文章，但从不回看
- 笔记分散在 Flomo、飞书、微信收藏等多个地方
- 想要一个能「记住」你所有知识的 AI 助手

---

## 5 分钟快速开始

### 1. 安装依赖

```bash
# 克隆或解压项目后，进入目录
cd Moos-share

# 安装依赖
pip install -e .
```

### 2. 配置 MCP（必需）

在 Claude Code 或 CodeBuddy 中添加 MCP 配置：

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

配置完成后，你就可以在对话中使用以下功能：

- `collect_content` - 收集网页内容
- `query_context` - 查询知识库
- `manage_topic` - 管理主题分类

### 3. 试试收集一篇文章

在对话中输入：

```
帮我收集这篇文章：https://example.com/article
```

AI 会自动：
1. 提取文章标题、正文、作者
2. 保存到 `data/context/__collected/`
3. 生成 Obsidian 格式的 Markdown 文件

### 4. 查询你的知识库

```
我收藏过关于 AI Agent 的文章吗？
```

AI 会搜索你的知识库并返回相关内容。

---

## 进阶配置

### 配置飞书同步（可选）

如果你想同步飞书多维表格的数据：

1. **创建飞书应用**
   - 访问 [飞书开放平台](https://open.feishu.cn/app)
   - 创建「企业自建应用」
   - 获取 `App ID` 和 `App Secret`

2. **编辑配置文件**
   ```bash
   cp config.example.yaml config.yaml
   # 编辑 config.yaml，填入你的飞书配置
   ```

3. **配置权限**
   - 在飞书后台，给应用添加「多维表格」权限
   - 将应用添加到你的多维表格

4. **运行同步**
   ```bash
   python -m pa.cli sync
   ```

### 自定义主题分类

编辑 `config.yaml` 中的 `context.core_topics`：

```yaml
context:
  core_topics:
    my_topic:
      name: "我的主题"
      description: "主题描述"
      keywords: ["关键词1", "关键词2"]
```

内容会根据关键词自动分类。

---

## 文件结构

```
Moos-share/
├── src/pa/                 # 核心源代码
│   ├── extractors/         # 网页内容提取
│   ├── formatters/         # Obsidian 格式化
│   ├── router/             # 内容路由引擎
│   └── mcp_server.py       # MCP 服务入口
├── skills/                 # Skill 扩展
│   └── huashu-slides/      # 花述 PPT 生成
├── data/
│   ├── context/            # 知识库（Obsidian 格式）
│   │   ├── __created/      # 原创内容
│   │   └── __collected/    # 收集的内容
│   └── raw/                # 原始数据
├── config.example.yaml     # 配置模板
├── config.yaml             # 你的配置（需自行创建）
└── pyproject.toml          # 依赖配置
```

---

## 常见问题

### Q: 需要技术基础吗？
不需要。MCP 功能可以在 Claude Code / CodeBuddy 中直接使用，不需要写代码。

### Q: 数据存储在哪里？
所有数据都保存在本地 `data/` 目录，完全由你掌控。

### Q: 可以和其他笔记软件联动吗？
可以。`data/context/` 是标准的 Markdown 文件，可以被 Obsidian、Notion 等软件读取。

### Q: 飞书同步是必需的吗？
不是。飞书同步是可选功能，不影响核心的网页收集和知识库查询功能。

---

## 技术架构

```
URL Input
    │
    ▼
┌─────────────────┐
│  Web Extractor  │  ← 自动提取正文、元数据
│  (trafilatura)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Topic Router   │  ← 智能分类
│  (关键词匹配)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Obsidian        │  ← 生成 Markdown
│ Formatter       │
└────────┬────────┘
         │
         ▼
    data/context/   ← 知识库
```

---

## 了解更多

- **核心文章**：《我与AI共建了一套个人知识操作系统》
- **设计理念**：与其追逐各种 AI 工具，不如自建一个知识中枢

---

## 注意事项

- `config.yaml` 中的配置已被脱敏，需要填入你自己的值
- 个人笔记数据未包含在此分享包中
- 如需使用飞书同步功能，需要自行配置 API 凭证
