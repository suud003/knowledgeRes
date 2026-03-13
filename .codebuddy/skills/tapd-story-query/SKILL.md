---
name: tapd-story-query
description: TAPD 需求查询与修改 Skill，用于 PUBG Mobile 项目的需求列表查询和字段修改。当用户提到 查询需求、需求列表、版本号查询、负责策划查询、需求状态、修改需求、stories_get、stories_update、需求字段修改 等关键词时，使用此 Skill。
---

# TAPD 需求查询与修改 Skill

> **前置依赖**：字段映射和 MCP 调用链路参见 `tapd-core` Skill。本 Skill 中使用的自定义字段名（如 `custom_field_79`）和 MCP 调用方式（lookup_tool_param_schema + proxy_execute_tool）均定义在 tapd-core 中。
>
> **人员 ID 匹配**：涉及处理人（`owner`）、负责策划（`custom_field_79`）、前台开发（`custom_field_82`）、后台开发（`custom_field_78`）等人员字段时，若用户提供中文名、拼音或简写，必须先加载 `tapd-core/references/people-mapping.md` 进行自动匹配，确认企微英文ID后再调用 API。匹配规则见 tapd-core「人员 ID 自动匹配」章节。
>
> **版本号转换**：用户提到版本号时（如 `430`、"当前版本"），必须先通过 `tapd-core/references/version-schedule.md` 转换为完整版本号（如 `4.3.0`），再使用需求的 `version` 字段查询。⚠️ 需求版本字段是 `version`，不是 `version_report`。

## Overview

PUBG Mobile 项目的 TAPD 需求（Story）查询与修改操作。支持按版本号、负责策划、状态三要素快速查询需求列表，以及修改需求的任意字段。

## ⚡ 典型查询场景 → 确定性执行（优先匹配）

> **核心原则**：用户的查询意图可以通过下方场景表直接映射到确定的参数组合，**无需探索、无需多余的工具调用**。匹配到场景后，直接按对应的参数执行 `proxy_execute_tool`（已知工具名时跳过 `lookup_tapd_tool`，仅需 `lookup_tool_param_schema` 获取 schema）。

### 场景匹配表

| 用户说法 | 场景 | 确定参数 |
|---------|------|---------|
| "查下我430的需求" / "我430的需求情况" | 查我某版本的需求列表 | `version`=转换后版本号, `custom_field_79`=用户RTX, `with_v_status`=`1` |
| "我430开发中的需求" / "430还在开发的需求" | 查某版本开发中的需求 | `version`=转换后版本号, `custom_field_79`=用户RTX, `status`=`developing`, `with_v_status`=`1` |
| "我430还没转测的需求" / "430规划中的需求" | 查某版本规划中的需求 | `version`=转换后版本号, `custom_field_79`=用户RTX, `status`=`planning`, `with_v_status`=`1` |
| "我的需求情况" / "我当前版本的需求" | 查当前开发版本我的需求 | `version`=当前开发版本, `custom_field_79`=用户RTX, `with_v_status`=`1` |

### 确定性执行流程（3步完成，不可多余）

**用户说"查下我430的需求"时的完整执行：**

1. **版本转换**：`430` → 查 `tapd-core/references/version-schedule.md` → `4.3.0`
2. **参数确定**：
   - `workspace_id`: `20360302`（固定值）
   - `version`: `4.3.0`（需求版本字段，不是 `version_report`）
   - `custom_field_79`: `tianyishao`（"我的"= 负责策划是我，**不带分号**）
   - `with_v_status`: `1`（获取中文状态）
3. **执行**：`lookup_tool_param_schema("stories_get")` → `proxy_execute_tool`：
```json
{
  "tool_name": "stories_get",
  "tool_args": {
    "workspace_id": "20360302",
    "version": "4.3.0",
    "custom_field_79": "tianyishao",
    "with_v_status": "1"
  }
}
```

> ⚠️ **需求查询中"我的"= 负责策划（`custom_field_79`）**，与缺陷不同（缺陷的"我的"= 处理人 `current_owner`）。
>
> ⚠️ **禁止行为**：不要先调用 `lookup_tapd_tool` 搜索工具、不要先查字段配置、不要分多次探索性调用。所有字段名和值在本 Skill 中已明确定义。

## 一、三要素查询需求

通过版本号 + 负责策划 + 状态组合查询需求列表。

**工具链路**：`lookup_tool_param_schema("stories_get")` → `proxy_execute_tool`

**参数模板**：

```json
{
  "tool_name": "stories_get",
  "tool_args": {
    "workspace_id": "20360302",
    "version": "<版本号>",
    "custom_field_79": "<负责策划RTX>",
    "status": "<状态代码>",
    "with_v_status": "1"
  }
}
```

**常用状态值**（需求）：
- `planning` - 规划中
- `developing` - 开发中
- `for_test` - 转测试
- `testing` - 测试中
- `resolved` - 已实现
- `closed` - 已关闭

## 二、修改需求

**工具链路**：`lookup_tool_param_schema("stories_update")` → `proxy_execute_tool`

**参数模板**：

```json
{
  "tool_name": "stories_update",
  "tool_args": {
    "workspace_id": "20360302",
    "id": "<需求ID>",
    "<字段名>": "<新值>"
  }
}
```

## 三、增量修改需求描述

### 场景：用户要求对现有需求做增量补充

执行原则：
1. 先用 `stories_get` 拉取当前 `description`
2. 定位对应章节（如需求二/需求三/需求四）
3. 只在对应章节插入补充内容
4. 保持原结构不重写整单
5. 如存在总单+子单，需判断是否双边同步

## 四、特殊限制：红字标注

当用户要求"用红色标注"时：
- 明确说明：TAPD 不支持可靠红字
- 自动回退为：`**加粗** + 【重点补充】`
- 若用户接受，再执行更新

## 五、需求更新输出要求

更新需求内容后，输出必须包含：
1. 修改的是哪几个章节
2. 是否为增量插入还是文末追加
3. 需求链接
4. 若存在限制（如红字不支持、链接回显不稳定），需明确告知

## 操作示例

### 示例1：查询 4.3.0 版本 tianyishao 的所有需求

```json
{
  "tool_name": "stories_get",
  "tool_args": {
    "workspace_id": "20360302",
    "version": "4.3.0",
    "custom_field_79": "tianyishao",
    "with_v_status": "1"
  }
}
```

### 示例2：查询 4.3.0 版本开发中的需求

```json
{
  "tool_name": "stories_get",
  "tool_args": {
    "workspace_id": "20360302",
    "version": "4.3.0",
    "custom_field_79": "tianyishao",
    "status": "developing",
    "with_v_status": "1"
  }
}
```

### 示例3：修改需求的处理人

```json
{
  "tool_name": "stories_update",
  "tool_args": {
    "workspace_id": "20360302",
    "id": "1020360302131247179",
    "owner": "newowner;"
  }
}
```

> ⚠️ `owner` 字段值末尾必须带分号。
