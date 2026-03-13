# FolderDoc-to-Wiki Skill

## 描述

将 `raw data/type_record/` 目录下的 FolderDoc 系列 Markdown 文档改写为精简的 WIKI 文档，并按代码目录结构映射到 iWiki 的"5.1 偷走脑腐"文档树中。每个 `.lua` 文件对应一个 WIKI 子文档，每个代码目录对应一个 WIKI 文件夹。

## 触发条件

当用户提到以下关键词时触发：
- "处理 FolderDoc"、"FolderDoc 写到 WIKI"、"FolderDoc 整合到 WIKI"
- "处理所有剩余的 FolderDoc"、"把文档写进 WIKI"
- 指定某个 FolderDoc 文件名（如 "FolderDoc_02"）

## 参考资料

执行前必须读取以下参考文件：
1. `references/wiki_mapping.md` — WIKI ID 常量和文件夹/文档映射关系
2. `references/rewrite_style_guide.md` — 改写风格规范
3. `references/sample_rewrite.md` — 改写前后对照样板

## 执行流程

### 第一步：确定处理范围

1. 用户指定某个 FolderDoc 文件名 → 仅处理该文件
2. 用户说"处理所有/剩余" → 处理 FolderDoc_00 + FolderDoc_02 ~ FolderDoc_05（跳过已完成的 01）
3. 读取 `references/wiki_mapping.md` 获取所有 WIKI ID 常量

### 第二步：读取并解析 FolderDoc

1. 从 `raw data/type_record/` 读取目标 FolderDoc md 文件
2. 解析标题层级：
   - `## 一、二、三、...` → 代码目录/文件夹
   - `### 1. 2. 3. ...` → 具体的 `.lua` 文件
3. 提取每个文件的内容段落（职责、属性、函数列表等）

### 第三步：在 WIKI 中创建文件夹结构

1. 使用 `getSpacePageTree` 查询目标父级下已有的子文档/文件夹
2. 已存在的文件夹 → 记录 docid 并复用
3. 不存在的文件夹 → 使用 `createDocument(contenttype="FOLDER", body=" ")` 创建
4. 记录所有新建/已有文件夹的 docid

### 第四步：创建/更新 WIKI 文档

对每个 `.lua` 文件段落：

1. **改写内容**：按 `references/rewrite_style_guide.md` 规范改写
2. **创建文档**（两步法 [[memory:jgsczorw]]）：
   - 第一步：`createDocument(spaceid=4010703137, parentid=<父文件夹ID>, title="<文件名>", contenttype="MD", body=" ")`
   - 第二步：`saveDocument(docid=<新文档ID>, title="<文件名>", body="<改写后的Markdown>")`
3. **更新已有文档**：直接 `saveDocument`

### 第五步：进度反馈与汇总

每处理完一个 FolderDoc，输出创建清单：
```
✅ FolderDoc_XX 处理完成
- 创建文件夹: N 个
- 创建文档: M 个
- 更新文档: K 个
- 失败: F 个
```

## 改写规则摘要

### 通用结构

```markdown
# 职责
一句话描述文件的核心职责

# [章节名]（按文件类型选择）
表格/列表/流程图等

# 关键流程（如有 mermaid 图则保留）
```

### 按文件类型的改写模板

| 文件类型 | 章节顺序 |
|---------|---------|
| Config 配置文件 | `# 职责` → `# 主要配置项`（含枚举表、参数表） |
| Core 核心类 | `# 职责` → `# Feature 注入`(如有) → `# RPC 方法`(如有) → `# 值复制属性`(如有) → `# 核心函数`(表格) → `# 关键流程`(如有) |
| Actor 实体类 | `# 职责` → `# 核心属性`(表格) → `# 网络同步属性`(如有) → `# 函数分类总览`(表格) → `# 关键流程`(如有) |
| Feature 功能类 | `# 职责` → `# 挂载对象` → `# RPC 方法`(表格) → `# 核心函数`(表格) → `# 关键流程`(如有) |
| SubSystem 子系统 | `# 职责` → `# 核心函数`(分类表格) → `# 关键流程`(如有) |
| Handler 协议处理 | `# 职责` → `# 协议函数列表`(表格) |
| UI 界面类 | `# 职责` → `# UI 元素绑定`(如有) → `# 核心函数`(表格) → `# 交互流程`(如有) |
| Utils 工具类 | `# 职责` → `# 函数列表`(表格) |

### 精简原则

1. **蓝图路径**：简化为"详情查看 lua 文件中的 XXX 字段"
2. **超长代码片段**：只保留关键结构示例（10行以内），移除逐行解读
3. **500行以上的描述**：重点保留职责概述、属性表、函数列表表格、关键流程图
4. **mermaid/ASCII 图**：完整保留（iWiki 支持 mermaid）
5. **"没看懂"标记**：在 WIKI 文档标题中保留（如 `RoundFlowTriggersCfg.lua（没看懂）`）
6. **函数表格格式**：`| 函数名 | 说明 |`，移除参数列和返回值列（除非特别重要）

## WIKI 配置常量

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 个人空间 ID | 4010703137 | iWiki 空间 |
| 偷走脑腐 | 4018569240 | 5.1 偷走脑腐 |
| 快速开始 | 4018569234 | 快速开始文档 |
| API参考手册 | 4018569206 | API参考手册根文件夹 |
| GamePlay/ | 4018569259 | GamePlay 文件夹 |
| Config/ | 4018577057 | Config 文件夹 |
| Dev/ | 4018569491 | Dev 文件夹 |
| Tools/ | 4018575600 | Tools 文件夹 |

## 错误处理

1. 文档创建失败 → 记录错误日志但继续处理下一个
2. 文档已存在 → 使用 `saveDocument` 更新而非重复创建
3. 权限问题 → 提示用户检查 iWiki 权限设置
