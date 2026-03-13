# FileDoc 文档映射配置

## 映射表

| FileDoc 文件名 | 类名 | iWiki 文档标题 | iWiki docid | 所在文件夹 docid | 处理状态 |
|---------------|------|--------------|-------------|----------------|---------|
| FileDoc_MonsterBaseActor.md | MonsterBaseActor | MonsterBaseActor.lua | 4018588599 | Actor/4018588519 | 已完成 |
| FileDoc_MonsterActor.md | MonsterActor | MonsterActor.lua | 4018588605 | Actor/4018588519 | 已完成 |
| FileDoc_MonsterFactoryActor.md | MonsterFactoryActor | MonsterFactoryActor.lua | 4018588610 | Actor/4018588519 | 已完成 |

## 说明

### 映射规则

1. **文件名提取类名**：`FileDoc_{类名}.md` → `{类名}`
2. **iWiki 文档标题**：`{类名}.lua`
3. **查找 iWiki 文档**：在"偷走脑腐"API 参考手册文档树（根 docid: 4018569206）下搜索同名文档

### 如何查找 iWiki 上的同名文档

当新增 FileDoc 需要映射时，按以下步骤定位 iWiki 目标文档：

1. **从 FileDoc 中提取文件路径**：读取 FileDoc 中"文件概览"表格的"文件路径"字段，确定该 lua 文件所在的代码目录
2. **推断 iWiki 文件夹**：根据代码目录与 iWiki 文档树的对应关系，确定所在文件夹的 docid
3. **遍历文件夹**：使用 `getSpacePageTree(parentid=文件夹docid)` 获取该文件夹下的所有文档
4. **匹配文档标题**：在返回的文档列表中查找标题为 `{类名}.lua` 的文档，记录其 docid

### 已知的 iWiki 文件夹映射

以下是 API 参考手册下已知的文件夹结构（根 docid: 4018569206）：

| 代码目录 | iWiki 文件夹名 | 文件夹 docid |
|---------|--------------|-------------|
| GamePlay/Actor/ | Actor | 4018588519 |

> 注意：随着更多 FileDoc 的加入，此表会持续更新。如遇到未知文件夹，需先通过 `getSpacePageTree` 遍历确认。

### 处理状态说明

| 状态 | 说明 |
|------|------|
| 待处理 | 已记录映射关系，尚未写入 iWiki |
| 已完成 | 已按改写规范处理并写入 iWiki |
| 待确认 | iWiki 上找不到同名文档，需用户确认 |
| 跳过 | 用户指示不处理该文件 |
