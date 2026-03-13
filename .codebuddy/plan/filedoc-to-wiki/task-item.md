# 实施计划：FileDoc-to-Wiki 单文件文档映射

## 前置信息

- **iWiki 空间 ID**：4010703137
- **API 参考手册根 docid**：4018569206
- **MonsterBaseActor.lua 目标 docid**：4018588599（位于 GamePlay/Actor/4018588519）
- **FileDoc 源目录**：`raw data/type_record/FileDoc_*.md`
- **已有 Skill 参考**：`.codebuddy/skills/folderdoc-to-wiki/`
- **已有改写规范**：`.codebuddy/skills/folderdoc-to-wiki/references/rewrite_style_guide.md`

---

- [ ] 1. 创建 filedoc-to-wiki Skill 主文件（SKILL.md）
   - 在 `.codebuddy/skills/filedoc-to-wiki/` 目录下创建 `SKILL.md`
   - 参照 `folderdoc-to-wiki/SKILL.md` 的结构编写，包含：触发条件、执行流程、改写规范引用、工具调用说明
   - 触发方式：指定文件名（"处理 FileDoc_XXX"）或批量（"处理所有 FileDoc"）
   - 核心流程：提取类名 → 查找 iWiki 同名文档 → 读取 FileDoc → 改写 → saveDocument 写入
   - 找不到同名文档时的兜底策略：提示用户确认父文件夹
   - _需求：2.1、2.2、2.3、2.4、2.5、2.6、2.7_

- [ ] 2. 创建 FileDoc 改写规范扩展文件
   - 在 `.codebuddy/skills/filedoc-to-wiki/references/` 下创建 `filedoc_rewrite_guide.md`
   - 引用 `folderdoc-to-wiki/references/rewrite_style_guide.md` 作为基础
   - 补充 FileDoc 特有的改写规则：保留详细深度、文件概览→职责转化、依赖关系保留、数据结构完整表格、函数分类保留、mermaid 流程图保留、设计说明保留
   - 定义 FileDoc 输出模板结构：职责 → 文件属性 → 依赖关系 → 核心属性/数据结构 → 网络同步属性 → 函数分类总览 → 核心流程 → 关键设计说明
   - _需求：4.1、4.2、4.3、4.4、4.5、4.6、4.7、4.8_

- [ ] 3. 创建文档映射配置文件（filedoc_mapping.md）
   - 在 `.codebuddy/skills/filedoc-to-wiki/references/` 下创建 `filedoc_mapping.md`
   - 包含映射表：FileDoc 文件名 | 类名 | iWiki 文档标题 | iWiki docid | 所在文件夹 docid | 处理状态
   - 预填已知条目：`FileDoc_MonsterBaseActor.md` → `MonsterBaseActor.lua`（docid: 4018588599，文件夹: Actor/4018588519，状态: 待处理）
   - 说明如何查找 iWiki 上的同名文档（通过 getSpacePageTree 遍历已知文件夹）
   - _需求：3.1、3.2、3.3_

- [ ] 4. 读取 FileDoc_MonsterBaseActor.md 并按改写规范整理内容
   - 读取 `raw data/type_record/FileDoc_MonsterBaseActor.md` 的完整内容
   - 按照任务 2 中定义的 FileDoc 改写规范对内容进行格式调整：
     - "文件概览"表格 → `# 职责` + `# 文件属性` 章节
     - 保留"依赖关系"完整内容
     - 保留"数据结构"完整表格
     - 保留"函数列表"分类结构
     - 保留所有 mermaid 流程图
     - 保留"关键设计说明"章节
   - 确保改写后的 Markdown 格式符合 iWiki 渲染要求
   - _需求：1.1、1.2、1.3、1.4_

- [ ] 5. 将改写后的内容写入 iWiki MonsterBaseActor.lua 文档
   - 使用 `saveDocument(docid=4018588599, title="MonsterBaseActor.lua", body=改写后内容)` 写入 iWiki
   - 验证写入成功
   - 输出确认信息（文档标题 + docid + 文档链接）
   - _需求：1.5、1.6_

- [ ] 6. 更新映射配置文件的处理状态
   - 将 `filedoc_mapping.md` 中 `FileDoc_MonsterBaseActor.md` 的状态从"待处理"更新为"已完成"
   - _需求：3.4_
