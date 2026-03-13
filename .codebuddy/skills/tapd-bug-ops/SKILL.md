---
name: tapd-bug-ops
description: TAPD 缺陷操作 Skill，用于 PUBG Mobile 项目的 Bug 查询、详情分析、关联需求查询和缺陷修改。当用户提到 bug查询、缺陷查询、未处理bug、待处理bug、bug分析、bug详情、关联需求、bug关联、修改缺陷、bugs_get、bugs_update、缺陷状态 等关键词时，使用此 Skill。
---

# TAPD 缺陷操作 Skill

> **前置依赖**：字段映射和 MCP 调用链路参见 `tapd-core` Skill。本 Skill 中使用的自定义字段名（如 `custom_field_9`）和 MCP 调用方式（lookup_tool_param_schema + proxy_execute_tool）均定义在 tapd-core 中。
>
> **人员 ID 匹配**：涉及处理人（`current_owner`）、负责策划（`custom_field_9`）等人员字段时，若用户提供中文名、拼音或简写，必须先加载 `tapd-core/references/people-mapping.md` 进行自动匹配，确认企微英文ID后再调用 API。匹配规则见 tapd-core「人员 ID 自动匹配」章节。
>
> **版本号转换**：用户提到版本号时（如 `430`、"当前版本"），必须先通过 `tapd-core/references/version-schedule.md` 转换为完整版本号（如 `4.3.0`），再使用缺陷的 `version_report` 字段查询。⚠️ 缺陷版本字段是 `version_report`，不是 `version`。

## Overview

PUBG Mobile 项目的 TAPD 缺陷（Bug）完整操作闭环，包括按多维条件查询缺陷列表、获取 Bug 详情并进行结构化分析、查找 Bug 关联的需求单、修改缺陷字段。

## ⚡ 典型查询场景 → 确定性执行（优先匹配）

> **核心原则**：用户的查询意图可以通过下方场景表直接映射到确定的参数组合，**无需探索、无需多余的工具调用**。匹配到场景后，直接按对应的参数执行 `proxy_execute_tool`（已知工具名时跳过 `lookup_tapd_tool`，仅需 `lookup_tool_param_schema` 获取 schema）。

### 场景匹配表

| 用户说法 | 场景 | 确定参数 |
|---------|------|---------|
| "分析下我430版本的缺陷情况" / "我430的bug情况" | 查我某版本的待处理缺陷 | `version_report`=转换后版本号, `current_owner`=用户RTX+`;`, `status`=`new\|in_progress\|reopened` |
| "我430版本还有多少bug" / "430我还有多少未处理的bug" | 同上 | 同上 |
| "430版本有哪些bug" / "430的缺陷列表" | 查某版本全部待处理缺陷（不限人） | `version_report`=转换后版本号, `status`=`new\|in_progress\|reopened` |
| "我待处理的bug" / "需要我处理的bug" | 查当前开发版本我的待处理缺陷 | `version_report`=当前开发版本, `current_owner`=用户RTX+`;`, `status`=`new\|in_progress\|reopened\|audit_reject` |
| "我负责的430bug" / "我是负责策划的430缺陷" | 查我作为负责策划的缺陷 | `version_report`=转换后版本号, `custom_field_9`=用户RTX, `status`=`new\|in_progress\|reopened` |

### 确定性执行流程（3步完成，不可多余）

**用户说"分析下我430版本的缺陷情况"时的完整执行：**

1. **版本转换**：`430` → 查 `tapd-core/references/version-schedule.md` → `4.3.0`
2. **参数确定**：
   - `workspace_id`: `20360302`（固定值）
   - `version_report`: `4.3.0`（缺陷版本字段，不是 `version`）
   - `current_owner`: `tianyishao;`（"我的"= 处理人是我，末尾带分号）
   - `status`: `new|in_progress|reopened`（待处理状态：新建、接受/处理中、重新打开）
3. **执行**：`lookup_tool_param_schema("bugs_get")` → `proxy_execute_tool`：
```json
{
  "tool_name": "bugs_get",
  "tool_args": {
    "workspace_id": "20360302",
    "version_report": "4.3.0",
    "current_owner": "tianyishao;",
    "status": "new|in_progress|reopened"
  }
}
```

> ⚠️ **禁止行为**：不要先调用 `lookup_tapd_tool` 搜索工具、不要先查字段配置、不要分多次探索性调用。所有字段名和值在本 Skill 中已明确定义。

## 一、查询缺陷

通过版本号 + 负责策划/处理人 + 状态组合查询缺陷列表。根据 tapd-core 中的语义映射表选择正确的查询字段。

**工具链路**：`lookup_tool_param_schema("bugs_get")` → `proxy_execute_tool`

**参数模板（按负责策划查）**：

```json
{
  "tool_name": "bugs_get",
  "tool_args": {
    "workspace_id": "20360302",
    "version_report": "<版本号>",
    "custom_field_9": "<负责策划RTX>",
    "status": "<状态代码>"
  }
}
```

**参数模板（按处理人查 — "未处理/待处理"）**：

```json
{
  "tool_name": "bugs_get",
  "tool_args": {
    "workspace_id": "20360302",
    "version_report": "<版本号>",
    "current_owner": "<用户RTX>;",
    "status": "new|in_progress|reopened|audit_reject"
  }
}
```

> ⚠️ `bugs_get` 不支持 `with_v_status` 参数。如需按中文状态查询，使用 `v_status` 字段（如 `v_status: "新建|处理中"`）。

**常用状态值**（缺陷）：
- `new` - 新建
- `in_progress` / `open` - 处理中
- `resolved` - 已解决
- `reopened` - 重新打开
- `audit_reject` - 审核驳回
- `verified` - 已验证
- `closed` - 已关闭
- `rejected` - 已拒绝
- `status_2` - 已转需求（属于关闭状态，无需处理）

> ⚠️ `status_2`（已转需求）表示该 bug 已转为需求单处理，属于关闭状态，查询未处理 bug 时应排除此状态。

## 二、Bug 详情获取与内容分析

查询到缺陷列表后，获取每个 bug 的详细描述进行结构化分析。

**步骤**：

1. 使用 `bugs_get` 获取详情，在 `fields` 参数中包含 `description`：

```json
{
  "tool_name": "bugs_get",
  "tool_args": {
    "workspace_id": "20360302",
    "id": "<缺陷ID>",
    "fields": "id,title,description,severity,status,current_owner,reporter,version_report,module,frequency"
  }
}
```

2. 对返回的 `description` 内容进行结构化分析，输出以下维度：

| 分析维度 | 说明 |
|---------|------|
| **问题类型** | UI布局 / 功能逻辑 / 数据异常 / 翻译问题 / 性能 / 崩溃 等 |
| **影响范围** | 单平台/双端、特定机型/通用、特定语言/全语言 |
| **复现难度** | 必现 / 高概率 / 偶现 / 难以复现 |
| **关联模块** | 从 `module` 字段和描述中提取所属功能模块 |
| **建议优先级** | P0(紧急) / P1(高) / P2(中) / P3(低)，综合严重度、复现率、影响面判断 |

## 三、Bug 关联需求查询

根据 bug 的版本号和内容，自动查找对应的需求单。采用两级策略：

**第一级：直接关联查询**（可能受权限限制）

使用 `get_bug_related_stories` 查询 TAPD 中已建立的关联关系：

```json
{
  "tool_name": "get_bug_related_stories",
  "tool_args": {
    "workspace_id": "20360302",
    "bug_id": "<缺陷ID>"
  }
}
```

> ⚠️ 当前 MCP token 可能无 `bugs::get_related_stories` 权限（返回 403）。此时自动回退到第二级。

**第二级：关键词搜索（主要策略）**

从 bug 的 `module`、`title` 中提取关键词，用 `stories_get` 按同版本 + 负责策划搜索：

```json
{
  "tool_name": "stories_get",
  "tool_args": {
    "workspace_id": "20360302",
    "version": "<与bug相同的版本号>",
    "custom_field_79": "<用户RTX>",
    "name": "<从bug标题/模块提取的关键词>",
    "with_v_status": "1"
  }
}
```

> **关键词提取策略**：
> 1. 从 `module` 字段去掉"系统-"前缀（如"系统-好友侧栏"→"好友"或"侧栏"）
> 2. 从 `title` 中提取功能名称（如"WOW"、"回流"、"智能助手"）
> 3. 如果第一个关键词无结果，尝试用更宽泛的关键词（如从"好友侧栏"→"WOW"）
> 4. 需求标题通常以"【V版本号】【模块】"格式开头，可据此匹配

## 四、修改缺陷

**工具链路**：`lookup_tool_param_schema("bugs_update")` → `proxy_execute_tool`

**参数模板**：

```json
{
  "tool_name": "bugs_update",
  "tool_args": {
    "workspace_id": "20360302",
    "id": "<缺陷ID>",
    "<字段名>": "<新值>"
  }
}
```

## 五、输出约束

当用户要求"分析 bug"时，不要把标题压缩成过短摘要。
优先展示 TAPD 原始标题，必要时再补一句中文归纳。

## 操作示例

### 示例1：查询 4.3.0 版本 tianyishao 负责的未关闭缺陷

```json
{
  "tool_name": "bugs_get",
  "tool_args": {
    "workspace_id": "20360302",
    "version_report": "4.3.0",
    "custom_field_9": "tianyishao",
    "status": "new|in_progress|resolved|reopened"
  }
}
```

### 示例2：查询需要 tianyishao 处理的待处理 bug（处理人是我）

```json
{
  "tool_name": "bugs_get",
  "tool_args": {
    "workspace_id": "20360302",
    "version_report": "4.3.0",
    "current_owner": "tianyishao;",
    "status": "new|in_progress|reopened|audit_reject"
  }
}
```

### 示例3：获取 bug 详情并分析

```json
{
  "tool_name": "bugs_get",
  "tool_args": {
    "workspace_id": "20360302",
    "id": "1020360302155127747",
    "fields": "id,title,description,severity,status,current_owner,reporter,version_report,module,frequency"
  }
}
```

> 获取到 description 后，按"二、Bug 详情获取与内容分析"的分析维度表输出结构化分析结果。

### 示例4：查询 bug 关联的需求单（关键词搜索）

```json
{
  "tool_name": "stories_get",
  "tool_args": {
    "workspace_id": "20360302",
    "version": "4.3.0",
    "custom_field_79": "tianyishao",
    "name": "好友侧栏",
    "with_v_status": "1"
  }
}
```

> 如果"好友侧栏"无结果，尝试用更宽泛的关键词如"WOW"重新搜索。

### 示例5：将某个缺陷状态改为已解决

```json
{
  "tool_name": "bugs_update",
  "tool_args": {
    "workspace_id": "20360302",
    "id": "1120360302155122519",
    "status": "resolved",
    "current_owner": "tianyishao;"
  }
}
```
