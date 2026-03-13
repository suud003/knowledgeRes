# Yogurt - 人机协作的知识操作系统

> 基于 MCP 协议的个人知识管理系统，内置丰富的自定义指令和 Skill 扩展。
> 同时支持 **CodeBuddy** 和 **Claude Code**。

## 项目结构

```
Moos-share/
├── .codebuddy/              # CodeBuddy 配置（原始）
│   ├── commands/            # 自定义指令（16 个）
│   ├── skills/              # Skill 扩展（15 个）
│   └── plan/                # 执行计划
├── .claude/                 # Claude Code 配置（适配层）
│   ├── commands/            # 自定义指令（兼容 .codebuddy/commands/）
│   └── plan/                # 执行计划
├── data/
│   ├── context/             # 知识库（Git 备份）
│   │   ├── __created/       # 原创内容
│   │   └── __collected/     # 收集内容
│   └── raw/                 # 原始数据（Git 忽略）
├── config.yaml              # 主题和 RSS 配置
└── CLAUDE.md                # 本文件
```

## Skill 系统说明

所有 Skill 定义存放在 `.codebuddy/skills/` 目录下，两套工具共用。
Claude Code 的命令文件（`.claude/commands/`）通过引用路径指向原始 Skill 文件。

当命令中指示"读取 `.codebuddy/skills/xxx/SKILL.md`"时，请直接读取该文件获取完整指引。

### Skill 列表

| Skill | 用途 | 位置 |
|-------|------|------|
| agent-browser | 浏览器自动化 | `.codebuddy/skills/agent-browser/` |
| competitive-ai-research | 竞品 AI 调研 | `.codebuddy/skills/competitive-ai-research/` |
| daily-weekly-report | 日报/周报/月报生成 | `.codebuddy/skills/daily-weekly-report/` |
| folderdoc-to-wiki | FolderDoc 转 Wiki | `.codebuddy/skills/folderdoc-to-wiki/` |
| iwiki-doc | iWiki 文档管理 | `.codebuddy/skills/iwiki-doc/` |
| note-sync | 笔记双写同步 | `.codebuddy/skills/note-sync/` |
| skill-creator | Skill 创建指南 | `.codebuddy/skills/skill-creator/` |
| tapd-bug-ops | TAPD 缺陷操作 | `.codebuddy/skills/tapd-bug-ops/` |
| tapd-core | TAPD 核心映射 | `.codebuddy/skills/tapd-core/` |
| tapd-story-create | TAPD 需求创建 | `.codebuddy/skills/tapd-story-create/` |
| tapd-story-query | TAPD 需求查询 | `.codebuddy/skills/tapd-story-query/` |
| tapd-story-writing | TAPD 需求写作规范 | `.codebuddy/skills/tapd-story-writing/` |
| type-record-parser | 打字记录解析器 | `.codebuddy/skills/type-record-parser/` |
| web-browser | Playwright 浏览器 | `.codebuddy/skills/web-browser/` |
| wow-whitepaper | WoW 白皮书写作 | `.codebuddy/skills/wow-whitepaper/` |

## 自定义指令

在 Claude Code 中通过 `/` 前缀使用，如 `/collect`、`/note`、`/news` 等。

### 知识管理指令
- `/collect <url> [topic]` - 收集文章到知识库
- `/note <内容> [topic]` - 快速添加笔记
- `/save <编号>` - 保存推送文章
- `/search <关键词> [topic]` - 搜索知识库
- `/news [方向]` - 查看今日资讯
- `/digest` - 生成周学习摘要
- `/topics` - 查看主题列表
- `/recent [days] [topic]` - 查看近期更新
- `/sync` - 同步数据源

### 实践框架指令
- `/plan [topic] [focus]` - 创建 Ship-Learn-Next 计划
- `/track <plan_id> <week>` - 记录迭代结果

### 工作效率指令
- `/generate_daily [日期]` - 生成日报
- `/generate_weekly [周次]` - 生成周报
- `/generate_monthly [月份]` - 生成月报
- `/baipishu <关键词>` - 白皮书功能点扩写
- `/competitive-research [target]` - 竞品调研

## MCP 工具

项目通过 MCP Server 提供以下工具（需配置 MCP 连接）：
- `list_topics` / `manage_topic` - 主题管理
- `add_note` - 添加笔记
- `collect_content` - 收集网页内容
- `query_context` / `search_recent` - 搜索知识库
- `create_ship_plan` / `track_iteration` - Ship-Learn-Next 计划
- `sync_data` - 数据同步
- `fetch_daily_digest` / `save_selected_articles` - RSS 资讯

## 用户身份

- 游戏技术策划 / AI Agent 研究者
- 关注领域：AI + 游戏交叉、PUBGM WoW（UGC 玩法编辑器）
- 工作工具：TAPD（项目管理）、iWiki（文档管理）

## 知识库主题

配置见 `config.yaml`，核心主题：personal / writing / tasks / preferences / reflection / product / work / reading / ideas / ai

## 约定

- 中文优先，技术术语保留英文
- 收集的英文内容自动翻译为中文
- 知识库内容使用 Markdown 格式
- 原创内容存 `__created/`，收集内容存 `__collected/`
- 本地优先，Git 版本控制
