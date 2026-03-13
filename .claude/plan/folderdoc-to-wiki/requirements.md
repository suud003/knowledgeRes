# 需求文档：FolderDoc-to-Wiki Skill

## 引言

PlanBT 项目有一套 FolderDoc 系列的 Markdown 技术文档（存放在 `raw data/type_record/` 目录下），这些文档按代码文件夹结构详细描述了项目中每个 Lua 文件的职责、核心属性、函数列表、配置参数等。

用户需要将这些 FolderDoc 文档的内容**改写精简**后，**按代码目录结构**映射到 iWiki 的"5.1 偷走脑腐（Demo showcase）"下的对应位置，每个 `.lua` 文件对应一个 WIKI 子文档，每个代码目录对应一个 WIKI 文件夹。

当前状态：
- `FolderDoc_00` → **尚未处理**，需要整合到"快速开始"文档中（用 `saveDocument` 更新已有文档内容）
- `FolderDoc_01` → 已手动整理为"API参考手册/ModConfig.lua + GamePlay/Config/(14个子文档) + Dev/ + Tools/"
- `FolderDoc_02`~`FolderDoc_05` → **尚未处理**，需要在"API参考手册"下创建对应的文件夹/文档结构

本 Skill 的目标是：读取指定的 FolderDoc md 文件，自动改写内容，并在 iWiki 中创建/更新对应的文档树结构。

---

## 需求

### 需求 1：读取并解析 FolderDoc 文档

**用户故事：** 作为一名开发者，我希望 Skill 能自动读取 `raw data/type_record/` 目录下的 FolderDoc md 文件，解析出文档结构（按 ## / ### 标题层级对应文件夹/文件），以便自动识别需要创建的 WIKI 文档树。

#### 验收标准

1. WHEN 用户指定一个或多个 FolderDoc 文件名 THEN Skill SHALL 从 `raw data/type_record/` 目录读取对应文件
2. WHEN 用户不指定文件名而是说"处理所有/剩余文档" THEN Skill SHALL 自动扫描目录下所有 `FolderDoc_*.md` 文件，并跳过已处理的文档（仅跳过 FolderDoc_01）
3. WHEN 读取文件成功 THEN Skill SHALL 解析出文档中的层级结构：
   - 一级标题（`## 一、`/`## 二、`等）对应代码目录/文件夹
   - 二级标题（`### 1.`/`### 2.`等）对应具体的 `.lua` 文件
   - 每个文件段落包含：职责描述、核心属性表、函数列表、配置参数等

### 需求 2：FolderDoc 到 WIKI 文档树的映射规则

**用户故事：** 作为一名开发者，我希望 Skill 能根据每个 FolderDoc 的内容自动确定 WIKI 中的文件夹/文档层级映射关系，以便在正确的位置创建对应的子文档。

#### 验收标准

1. WHEN 处理 `FolderDoc_00_Game_Overview.md` THEN Skill SHALL 读取已有的"快速开始"文档（ID: `4018569234`），将 FolderDoc_00 的内容改写后通过 `saveDocument` 整合/更新到该文档中
2. WHEN 处理 `FolderDoc_02_GameplayCore_Actor_Feature_Others.md` THEN Skill SHALL 在 "API参考手册/GamePlay/" 下创建以下子文件夹和文档：
   - `Core/` 文件夹 → 内含 PlanBTGameMode.lua、PlanBTPlayerController.lua 等子文档
   - `Actor/` 文件夹 → 内含 MonsterBaseActor.lua、MonsterActor.lua 等子文档
   - `Feature/` 文件夹 → 内含 MonsterInteractionFeature.lua、CoinFeature.lua 等子文档
   - `SubSystem/` 文件夹 → 内含 MonsterBaseSubsystem.lua 等子文档
   - `Skill/`、`Backpack/`、`Component/`、`Utils/` 等文件夹及子文档
3. WHEN 处理 `FolderDoc_03a_Client_Base.md` THEN Skill SHALL 在 "API参考手册/" 下创建 `Client/` 文件夹及其子结构（ClientLogicEntry.lua、交互UI文件、Config/、Handler/、SubSystem/、各子系统文件夹等）
4. WHEN 处理 `FolderDoc_03b_Client_UI.md` THEN Skill SHALL 在 "API参考手册/Client/UI/" 下创建各 UI 子文件夹和文档
5. WHEN 处理 `FolderDoc_04_DS.md` THEN Skill SHALL 在 "API参考手册/" 下创建 `DS/` 文件夹及其子结构
6. WHEN 处理 `FolderDoc_05_Dev_Common.md` THEN Skill SHALL 在 "API参考手册/" 下创建/更新 `Dev/`、`Common/` 文件夹及子文档
7. IF 目标文件夹或文档已存在 THEN Skill SHALL 使用 `saveDocument` 更新内容，而不是重复创建

### 需求 3：内容改写规则

**用户故事：** 作为一名开发者，我希望 Skill 在写入 WIKI 时能将原始 FolderDoc 内容改写为更适合在线阅读的精简版本，保留核心信息但移除冗余描述，以便 WIKI 文档简洁专业。

#### 验收标准

1. WHEN 创建每个 WIKI 子文档时 THEN Skill SHALL 按以下格式改写内容：
   - 以 `# 职责` 开头，一句话描述文件的核心职责
   - 然后是 `# 主要配置项` 或 `# 核心属性` 或 `# 函数列表` 等章节（视文件类型而定）
   - 表格保留原始数据但移除冗余说明列
   - 代码片段只保留关键示例，移除过长的完整代码
   - 蓝图路径等引擎资源路径信息简化为"详情查看 lua 文件中的 XXX 字段"
2. WHEN 处理 `FolderDoc_00` 整合到"快速开始"时 THEN Skill SHALL 保留"快速开始"文档已有的结构和风格，将 FolderDoc_00 中的新增内容（如玩法详述、系统模块说明、配置ID汇总等）以追加或合并的方式整合进去
3. WHEN 原始文档中的某个文件描述超过 500 行 THEN Skill SHALL 重点保留：职责概述、核心属性表、函数列表表格、关键流程说明，移除详细的逐行代码解读
4. WHEN 原始文档中包含 mermaid 流程图或 ASCII 图 THEN Skill SHALL 保留这些图（iWiki 支持 mermaid）
5. IF 原始文档中标注了"没看懂"或类似标记 THEN Skill SHALL 在 WIKI 文档标题中也保留该标记

### 需求 4：WIKI 文档创建流程

**用户故事：** 作为一名开发者，我希望 Skill 在创建 WIKI 文档时严格遵循两步创建规范（先创建空文档再写入内容），避免出现 JSON 渲染问题。

#### 验收标准

1. WHEN 创建新的 WIKI 文件夹 THEN Skill SHALL 使用 `createDocument` 创建 FOLDER 类型文档，`body` 传 `" "`
2. WHEN 创建新的 WIKI 文档 THEN Skill SHALL 分两步执行：
   - 第一步：`createDocument` 创建空文档（body 传 `" "`，contenttype 为 `"MD"`）
   - 第二步：`saveDocument` 写入改写后的 Markdown 正文内容
3. WHEN 更新已有文档（如"快速开始"）THEN Skill SHALL 直接使用 `saveDocument` 更新内容
4. WHEN 每个 FolderDoc 处理完成 THEN Skill SHALL 输出一份创建/更新的文档清单（文档标题 + WIKI ID + 状态）

### 需求 5：WIKI 配置常量

**用户故事：** 作为一名开发者，我希望 Skill 内置所有必要的 WIKI 文档 ID 常量，以便不需要每次手动查找和传入。

#### 验收标准

1. WHEN Skill 运行时 THEN Skill SHALL 使用以下固定配置：
   - 个人空间 ID：`4010703137`
   - "5.1 偷走脑腐"文档 ID：`4018569240`
   - "快速开始"文档 ID：`4018569234`
   - "API参考手册"文档 ID：`4018569206`
   - "GamePlay/"文件夹 ID：`4018569259`
   - "Config/"文件夹 ID：`4018577057`
2. WHEN 需要在 "GamePlay/" 下创建新文件夹（如 Core/、Actor/、Feature/ 等）THEN Skill SHALL 先检查是否已存在（通过 `getSpacePageTree` 查询），存在则复用 ID，不存在则创建

### 需求 6：执行模式与用户交互

**用户故事：** 作为一名开发者，我希望能通过简单的指令触发 Skill，一次处理一个或多个 FolderDoc 文件，并在执行过程中看到进度反馈。

#### 验收标准

1. WHEN 用户说"处理 FolderDoc_02"或"把 FolderDoc_02 写到 WIKI" THEN Skill SHALL 仅处理指定文件
2. WHEN 用户说"处理所有剩余的 FolderDoc" THEN Skill SHALL 处理 FolderDoc_00 + FolderDoc_02 ~ FolderDoc_05（跳过已完成的 FolderDoc_01）
3. WHEN 处理每个文件时 THEN Skill SHALL 分步骤报告进度：
   - "正在读取 FolderDoc_XX..."
   - "正在创建文件夹: GamePlay/Actor/"
   - "正在写入文档: MonsterBaseActor.lua"
   - "✅ FolderDoc_XX 处理完成，共创建 N 个文档"
4. IF 某个文档创建失败 THEN Skill SHALL 记录错误但继续处理下一个，最终汇总报告成功/失败数量

### 需求 7：FolderDoc 与 WIKI 的映射配置文件

**用户故事：** 作为一名开发者，我希望 Skill 维护一个映射配置文件（references），记录每个 FolderDoc 对应的 WIKI 目录结构，以便后续新增文档时可以扩展。

#### 验收标准

1. WHEN Skill 初始化时 THEN Skill 的 `references/` 目录下 SHALL 包含一个 `wiki_mapping.md` 文件，记录：
   - 每个 FolderDoc 文件名
   - 对应的 WIKI 父级文件夹 ID
   - 对应的 WIKI 文档树结构（文件夹名 → 子文档列表）
2. WHEN 用户新增了新的 FolderDoc 文件 THEN 用户可以更新映射配置来扩展 Skill 支持范围
