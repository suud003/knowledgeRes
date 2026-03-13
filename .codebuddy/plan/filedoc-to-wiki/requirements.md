# 需求文档：FileDoc-to-Wiki 单文件文档映射

## 引言

在之前的 `folderdoc-to-wiki` Skill 中，我们已经将 `raw data/type_record/` 目录下的 FolderDoc 系列（按代码目录整理的批量文档）改写并映射到了 iWiki 的"偷走脑腐"文档树中。现在需要处理另一种文档类型：**FileDoc（单文件详细解释文档）**。

FileDoc 的特征：
- 文件命名格式：`FileDoc_{类名}.md`（如 `FileDoc_MonsterBaseActor.md`）
- 每个 FileDoc 是对**单个 `.lua` 文件**的深度解析（通常 300~1000+ 行），包含文件概览、依赖关系、数据结构、函数列表、核心流程图等
- 在 iWiki 上已经存在同名的 `.lua` 文档（由 FolderDoc 批量创建时生成的精简版），FileDoc 需要将这些精简版**升级/覆盖**为详细版

核心目标：创建一个 `filedoc-to-wiki` Skill，将 `FileDoc_{类名}.md` 的内容按照改写规范整理后，写入 iWiki 上已有的 `{类名}.lua` 同名文档中。同时先立即处理当前唯一的 `FileDoc_MonsterBaseActor.md` 作为首个实例。

## 需求

### 需求 1：立即处理 FileDoc_MonsterBaseActor.md

**用户故事：** 作为一名开发者，我希望将 `FileDoc_MonsterBaseActor.md` 的详细内容写入 iWiki 上已有的 `MonsterBaseActor.lua` 文档中，以便团队成员能在 WIKI 上查阅这个核心类的完整文档。

#### 验收标准

1. WHEN 执行处理 FileDoc_MonsterBaseActor THEN 系统 SHALL 读取 `raw data/type_record/FileDoc_MonsterBaseActor.md` 的完整内容
2. WHEN 内容读取完成 THEN 系统 SHALL 按照已有的 `rewrite_style_guide.md` 改写规范对内容进行适度精简和格式调整（Actor 类型模板：职责 → 核心属性 → 网络同步属性 → 函数分类总览 → 关键流程）
3. IF FileDoc 中包含 mermaid 流程图 THEN 系统 SHALL 完整保留这些流程图（iWiki 支持 mermaid）
4. IF FileDoc 内容已经结构清晰（如 MonsterBaseActor.md 已有完整的表格、分类、流程图） THEN 系统 SHALL 尽量保留原有结构，仅做必要的格式适配
5. WHEN 内容改写完成 THEN 系统 SHALL 使用 `saveDocument(docid=4018588599)` 将改写后的内容写入 iWiki 上的 `MonsterBaseActor.lua` 文档
6. WHEN 写入完成 THEN 系统 SHALL 输出确认信息（包含文档标题和 docid）

### 需求 2：创建 filedoc-to-wiki Skill

**用户故事：** 作为一名开发者，我希望有一个通用的 `filedoc-to-wiki` Skill，以便未来新增更多 `FileDoc_{类名}.md` 文件时能通过 Skill 自动映射到 iWiki 对应文档。

#### 验收标准

1. WHEN Skill 创建完成 THEN 系统 SHALL 在 `.codebuddy/skills/filedoc-to-wiki/` 目录下包含 `SKILL.md` 主文件
2. WHEN Skill 被触发 THEN 系统 SHALL 支持以下触发方式：
   - 指定文件名：如 "处理 FileDoc_MonsterBaseActor"
   - 处理所有：如 "处理所有 FileDoc"、"把所有单文件文档写到 WIKI"
3. WHEN 处理某个 FileDoc THEN 系统 SHALL 自动从文件名提取类名（`FileDoc_{类名}.md` → `{类名}`）
4. WHEN 提取类名后 THEN 系统 SHALL 在 iWiki 文档树中搜索名为 `{类名}.lua` 的已有文档
5. IF iWiki 上找不到同名文档 THEN 系统 SHALL 提示用户确认是否需要手动创建或在指定文件夹下新建
6. IF iWiki 上找到同名文档 THEN 系统 SHALL 使用 `saveDocument` 将改写后的内容写入该文档
7. WHEN Skill 定义完成 THEN 系统 SHALL 包含 references 子目录，存放文档映射配置

### 需求 3：文档映射配置

**用户故事：** 作为一名开发者，我希望有一个映射配置文件记录 FileDoc 与 iWiki 文档的对应关系，以便快速定位目标文档并追踪处理状态。

#### 验收标准

1. WHEN 映射配置创建 THEN 系统 SHALL 在 `references/filedoc_mapping.md` 中维护映射表
2. WHEN 映射表创建 THEN 系统 SHALL 包含以下字段：FileDoc 文件名、类名、iWiki 文档标题、iWiki docid、所在文件夹 docid、处理状态
3. WHEN 新增 FileDoc 文件 THEN 系统 SHALL 支持将新文件追加到映射表中
4. WHEN 处理完成一个 FileDoc THEN 系统 SHALL 更新映射表中对应条目的状态为"已完成"

### 需求 4：改写规范适配

**用户故事：** 作为一名开发者，我希望 FileDoc 的改写规范能复用已有的 `folderdoc-to-wiki` 改写风格指南，同时针对 FileDoc 的特点做适当扩展，以便两种文档类型的 WIKI 输出风格一致。

#### 验收标准

1. WHEN 改写 FileDoc 内容 THEN 系统 SHALL 引用 `folderdoc-to-wiki/references/rewrite_style_guide.md` 作为基础改写规范
2. IF FileDoc 内容远超 FolderDoc 精简版（通常 3~10 倍内容量）THEN 系统 SHALL 保留 FileDoc 的详细程度（因为 FileDoc 本身就是深度文档，不应过度精简）
3. WHEN FileDoc 包含"文件概览"表格（文件路径/大小/继承关系/职责/运行端）THEN 系统 SHALL 将其转化为标准的 `# 职责` 章节 + 属性表
4. WHEN FileDoc 包含"依赖关系"章节 THEN 系统 SHALL 保留为 `# 依赖关系` 章节（FolderDoc 精简版通常没有此信息）
5. WHEN FileDoc 包含"数据结构"章节（详细的成员变量表）THEN 系统 SHALL 保留完整表格
6. WHEN FileDoc 包含"函数列表"按职责分类章节 THEN 系统 SHALL 保留分类结构和所有函数条目
7. WHEN FileDoc 包含"核心流程"mermaid 图 THEN 系统 SHALL 完整保留
8. WHEN FileDoc 包含"关键设计说明"章节 THEN 系统 SHALL 保留（这是 FileDoc 相比 FolderDoc 的增量价值）

## 边界情况

1. **FileDoc 对应的 iWiki 文档不存在**：提示用户手动指定父文件夹，或根据文件路径（FileDoc 中的"文件路径"字段）推断所在目录
2. **FileDoc 内容过长（超过 iWiki 单文档限制）**：目前未遇到，但如有需要可拆分为主文档 + 子文档
3. **多个 FileDoc 对应同一个类名但不同目录**：通过 FileDoc 中的"文件路径"字段区分
4. **FileDoc 格式不统一**：Skill 应具备容错能力，对不符合标准格式的 FileDoc 做最佳努力处理

## 技术限制

1. iWiki `saveDocument` 的 body 参数为 Markdown 格式
2. iWiki 支持 mermaid 渲染
3. 需遵循两步法创建文档 [[memory:jgsczorw]]（但本场景主要是更新已有文档，直接 saveDocument 即可）
4. 当前 `type_record/` 下只有 1 个 FileDoc 文件（`FileDoc_MonsterBaseActor.md`），但 Skill 设计需支持未来扩展

## 成功标准

1. `MonsterBaseActor.lua` 在 iWiki 上从精简版升级为详细版，内容覆盖文件概览、依赖、数据结构、函数列表、核心流程、设计说明
2. `filedoc-to-wiki` Skill 完整创建，可被后续对话触发使用
3. 映射配置文件完整，包含当前已知的 FileDoc 映射关系
