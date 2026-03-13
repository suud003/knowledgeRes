# FileDoc-to-Wiki Skill

## 描述

将 `raw data/type_record/` 目录下的 `FileDoc_{类名}.md` 单文件详细解释文档，按改写规范整理后写入 iWiki 文档树中对应的 `{类名}.lua` 同名文档。FileDoc 是对单个 `.lua` 文件的深度解析（通常 300~1000+ 行），包含文件概览、依赖关系、数据结构、函数列表、核心流程图等，比 FolderDoc 批量生成的精简版内容更详尽。

## 触发条件

当用户提到以下关键词时触发：
- "处理 FileDoc_XXX"、"FileDoc 写到 WIKI"、"单文件文档映射"
- "处理所有 FileDoc"、"把所有单文件文档写到 WIKI"
- 指定某个 FileDoc 文件名（如 "处理 FileDoc_MonsterBaseActor"）

## 参考资料

执行前必须读取以下参考文件：
1. `references/filedoc_mapping.md` — FileDoc 与 iWiki 文档的映射关系及处理状态
2. `references/filedoc_rewrite_guide.md` — FileDoc 改写规范（基于 folderdoc-to-wiki 的通用规范扩展）
3. `../folderdoc-to-wiki/references/rewrite_style_guide.md` — 基础改写风格规范（通用）

## 执行流程

### 第一步：确定处理范围

1. **指定文件**：用户指定某个 FileDoc 文件名 → 仅处理该文件
2. **批量处理**：用户说"处理所有/剩余 FileDoc" → 扫描 `raw data/type_record/FileDoc_*.md`，对照映射表跳过已完成的
3. 读取 `references/filedoc_mapping.md` 获取映射关系和处理状态

### 第二步：提取类名并查找 iWiki 目标文档

1. 从文件名提取类名：`FileDoc_{类名}.md` → `{类名}`
2. 在 `filedoc_mapping.md` 映射表中查找该类名：
   - **已有映射**：直接获取目标 docid
   - **无映射**：使用 `getSpacePageTree` 在 API 参考手册（docid: 4018569206）下的子文件夹中搜索 `{类名}.lua`
3. 如果 iWiki 上找不到同名文档：
   - 读取 FileDoc 中的"文件路径"字段，推断应归入的代码目录
   - 提示用户确认父文件夹 docid，或在推断的目录下新建文档

### 第三步：读取并改写 FileDoc

1. 读取 `raw data/type_record/FileDoc_{类名}.md` 完整内容
2. 按照 `references/filedoc_rewrite_guide.md` 改写规范进行格式调整：
   - "文件概览"表格 → `# 职责` + `# 文件属性` 章节
   - 保留"依赖关系"完整内容
   - 保留"数据结构"完整表格
   - 保留"函数列表"分类结构和所有函数条目
   - 保留所有 mermaid 流程图
   - 保留"关键设计说明"章节
3. 确保改写后的 Markdown 格式符合 iWiki 渲染要求

### 第四步：写入 iWiki

1. **更新已有文档**（主要场景）：
   - `saveDocument(docid=<目标docid>, title="{类名}.lua", body="<改写后的Markdown>")`
2. **新建文档**（仅当目标文档不存在时，两步法 [[memory:jgsczorw]]）：
   - 第一步：`createDocument(spaceid=4010703137, parentid=<父文件夹ID>, title="{类名}.lua", contenttype="MD", body=" ")`
   - 第二步：`saveDocument(docid=<新文档ID>, title="{类名}.lua", body="<改写后的Markdown>")`

### 第五步：更新映射配置与反馈

1. 更新 `references/filedoc_mapping.md` 中对应条目的处理状态为"✅ 已完成"
2. 如果是新文档，将新的映射关系追加到映射表中
3. 输出确认信息：
   ```
   ✅ FileDoc_{类名} 处理完成
   - 文档标题: {类名}.lua
   - iWiki docid: {docid}
   - 文档链接: https://iwiki.woa.com/p/{docid}
   ```

## 改写规则摘要

FileDoc 的改写不同于 FolderDoc 的精简改写——**FileDoc 应保留详细程度**，因为它本身就是深度文档。

### 核心差异
| 维度 | FolderDoc 改写 | FileDoc 改写 |
|------|--------------|-------------|
| 信息密度 | 大幅精简（10:1 压缩） | 适度整理（保留 80%+ 内容） |
| 依赖关系 | 通常移除 | 完整保留 |
| 数据结构 | 简化为关键属性 | 保留完整表格 |
| 函数列表 | 精简为 `函数名 + 说明` 两列表 | 保留分类结构和全部条目 |
| 流程图 | 保留 mermaid | 保留 mermaid |
| 设计说明 | 移除 | 完整保留 |

### 输出模板结构（Actor 类型示例）

```markdown
# 职责
一句话描述 + 补充说明

# 文件属性
| 属性 | 值 |
|------|-----|
| 文件路径 | ... |
| 继承关系 | ... |
| 运行端 | ... |

# 依赖关系
## 引用的模块
## 被引用的模块

# 核心属性与数据结构
（完整表格）

# 网络同步属性（如有）
（完整表格 + 回调说明）

# 函数分类总览
## [分类名]
| 函数名 | 说明 |
（保留全部函数条目）

# 核心流程
（mermaid 流程图完整保留）

# 关键设计说明
（保留设计决策、注意事项等）
```

## WIKI 配置常量

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 个人空间 ID | 4010703137 | iWiki 空间 |
| API 参考手册 | 4018569206 | API 参考手册根文件夹 |
| GamePlay/ | 4018569259 | GamePlay 文件夹 |
| Actor/ | 4018588519 | GamePlay/Actor 文件夹 |
| Config/ | 4018577057 | Config 文件夹 |
| Dev/ | 4018569491 | Dev 文件夹 |
| Tools/ | 4018575600 | Tools 文件夹 |

## 错误处理

1. **FileDoc 对应的 iWiki 文档不存在** → 提示用户确认父文件夹 docid，或根据文件路径推断目录后自动创建
2. **FileDoc 格式不符合预期** → 做最佳努力处理，按原文结构改写
3. **iWiki 写入失败** → 记录错误信息，提示用户重试
4. **多个 FileDoc 对应同一类名但不同目录** → 通过 FileDoc 中的"文件路径"字段区分
