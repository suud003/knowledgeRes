---
name: tapd-story-create
description: TAPD 创建需求 Skill，用于 PUBG Mobile 项目的新建需求单操作。当用户提到 创建需求、新建需求、建需求单、stories_create、提需求 等关键词时，使用此 Skill。包含分类确认、类型推断、参数填写和关键注意事项。
---

# TAPD 创建需求 Skill

> **前置依赖**：字段映射和 MCP 调用链路参见 `tapd-core` Skill。本 Skill 中使用的自定义字段名（如 `custom_field_79`、`custom_field_49`）和 MCP 调用方式（lookup_tool_param_schema + proxy_execute_tool）均定义在 tapd-core 中。
>
> **人员 ID 匹配**：涉及处理人（`owner`）、负责策划（`custom_field_79`）、前台开发（`custom_field_82`）、后台开发（`custom_field_78`）等人员字段时，若用户提供中文名、拼音或简写，必须先加载 `tapd-core/references/people-mapping.md` 进行自动匹配，确认企微英文ID后再调用 API。匹配规则见 tapd-core「人员 ID 自动匹配」章节。
>
> **版本号转换**：用户提到版本号时（如 `430`、"当前版本"），必须先通过 `tapd-core/references/version-schedule.md` 转换为完整版本号（如 `4.3.0`）。创建需求时版本字段为 `version`。

## Overview

PUBG Mobile 项目的 TAPD 需求单创建完整流程。包括分类 ID 确认、需求单类型智能推断、参数模板填写和关键注意事项。根据用户提供的信息智能填写字段，仅针对关键缺失项询问用户。

## ⚡ 典型创建场景 → 确定性执行（优先匹配）

> **核心原则**：用户创建需求时，根据已知信息直接填充参数，仅对**真正缺失的关键信息**询问用户。以下为典型场景和确定的参数来源。

### 场景匹配表

| 用户说法 | 场景 | 确定参数来源 |
|---------|------|------------|
| "帮我建个需求" / "创建需求单" | 最简创建 | 负责策划=用户RTX, 处理人=用户RTX, creator=用户RTX；需询问：需求标题、分类、描述内容 |
| "在440WOW下建个需求，处理人是XXX" | 指定分类+处理人 | 分类→查category_id, 处理人→人员匹配, 负责策划=用户RTX, creator=用户RTX |
| "创建一个配置单" | 指定类型 | `custom_field_49`=`配置单`，其他同上 |

### 确定性执行流程（4步完成）

**用户说"在440WOW下建个需求，标题XXX，处理人是linglingdai"时的完整执行：**

1. **人员匹配**：`linglingdai` → 查 `tapd-core/references/people-mapping.md` 确认有效
2. **分类ID获取**：用 `stories_get` 搜索同分类下已有需求获取 `category_id`：
```json
{
  "tool_name": "stories_get",
  "tool_args": {
    "workspace_id": "20360302",
    "name": "440",
    "limit": 50,
    "with_v_status": "1"
  }
}
```
> 从结果中提取 `category_id`（如 440WOW → `1020360302002729717`）

3. **参数确定**：
   - `workspace_id`: `20360302`（固定值）
   - `name`: 用户提供的需求标题
   - `category_id`: 上一步获取的分类ID
   - `description`: 用户提供的描述（可参考 `tapd-story-writing` 规范格式化）
   - `custom_field_49`: 根据内容智能推断（纯功能单/纯美术单/配置单等）
   - `custom_field_79`: 用户RTX（负责策划，**不带分号**）
   - `owner`: 处理人RTX + `;`（**必须带分号**）
   - `custom_field_78`: 后台开发RTX（未指定填 `""`）
   - `custom_field_82`: 前台开发RTX（未指定填 `""`）
   - `creator`: 用户RTX
4. **执行**：`lookup_tool_param_schema("stories_create")` → `proxy_execute_tool`：
```json
{
  "tool_name": "stories_create",
  "tool_args": {
    "workspace_id": "20360302",
    "name": "【440】【WOW】XXX",
    "category_id": "1020360302002729717",
    "description": "<需求描述>",
    "custom_field_49": "纯功能单",
    "custom_field_79": "tianyishao",
    "owner": "linglingdai;",
    "custom_field_78": "",
    "custom_field_82": "",
    "creator": "tianyishao"
  }
}
```

> ⚠️ **关键约束**：
> - `owner` 值末尾**必须带分号**，否则创建失败
> - **不要传入 `version` 参数**，会导致创建失败（版本号通过标题体现）
> - 前台/后台开发未指定时填空字符串 `""`（不是 null）
> - 创建成功后输出链接：`https://tapd.woa.com/tapd_fe/20360302/story/detail/{新建ID}`

## 标准创建流程

### 步骤1：确认分类 ID

若用户指定分类名称（如"440WOW"），先查询对应的 `category_id`：

```json
{
  "tool_name": "stories_get",
  "tool_args": {
    "workspace_id": "20360302",
    "name": "440",
    "limit": 50,
    "with_v_status": "1"
  }
}
```

> 从返回结果的 `category_id` 字段获取分类ID（如 `1020360302002729717` 对应440WOW）。

### 步骤2：智能推断需求单类型

根据需求内容自动判断 `custom_field_49` 的值：

| 需求内容特征 | 推断类型 |
|-------------|---------|
| 涉及召回、算法、策略、数据分析 | 纯功能单 |
| 涉及UI、美术资源、界面设计 | 纯美术单 |
| 同时涉及功能和美术 | 功能&美术单 |
| 涉及配置表、参数调整 | 配置单 |
| 涉及测试验证 | 测试单 |

可选值：`纯功能单` / `纯美术单` / `功能&美术单` / `音效&视频单` / `测试单` / `配置单`

### 步骤3：创建需求

**工具链路**：`lookup_tool_param_schema("stories_create")` → `proxy_execute_tool`

**参数模板**：

```json
{
  "tool_name": "stories_create",
  "tool_args": {
    "workspace_id": "20360302",
    "name": "<需求标题>",
    "category_id": "<分类ID>",
    "description": "<需求描述>",
    "custom_field_49": "<需求单类型>",
    "custom_field_79": "<负责策划RTX>",
    "owner": "<处理人RTX>;",
    "custom_field_78": "<后台开发RTX>",
    "custom_field_82": "<前台开发RTX>",
    "creator": "<创建人RTX>"
  }
}
```

### 步骤4：输出需求单链接

创建成功后，从返回的 `id` 构造需求单链接并输出给用户：

```
https://tapd.woa.com/tapd_fe/20360302/story/detail/{新建ID}
```

## 必填字段说明

| 字段 | API 字段名 | 填写策略 |
|-----|-----------|---------|
| 需求单类型 | `custom_field_49` | 根据内容智能推断 |
| 负责策划 | `custom_field_79` | 从用户信息中获取，或用户明确指定的策划RTX（不带分号） |
| 处理人 | `owner` | 用户指定的处理人RTX，末尾**必须带分号**（如 `tianyishao;`） |
| 后台开发 | `custom_field_78` | 用户指定的后台开发RTX，可为空字符串 `""` |
| 前台开发 | `custom_field_82` | 用户指定的前台开发RTX，可为空字符串 `""` |
| 创建人 | `creator` | 从用户信息中获取当前用户RTX |

## ⚠️ 关键注意事项

- **owner 字段值末尾必须带分号**，否则创建失败（如 `linglingdai;`）
- **不要传入 version 参数**，该参数会导致创建失败（版本号通过标题体现即可）
- 前台开发和后台开发可为空字符串 `""`（不是 null）
- 如果用户说"后台开发填XXX"，但未说明前台开发，则前台开发填空字符串

## 场景：创建总单 + 多个子单

适用场景：
- 用户说"新建1个总单，下面有多个子单"
- 用户明确要求"1个大点1个单"

执行流程：
1. 先确认总单标题、分类、需求单类型、处理人、后台开发
2. 创建总单，获取总单 `id`
3. 对每个大点分别创建子单，传入 `parent_id=<总单id>`
4. 子单标题按统一格式命名，例如：
   - `【440】【WOW】【精排优化】子单1-引入ABTest实验平台`
5. 最终输出总单链接 + 全部子单链接

## 处理人字段补充说明

1. `owner` 支持多处理人，多个 RTX 以分号分隔，且末尾必须保留分号。
2. 示例：
   - 单人：`linglingdai;`
   - 多人：`nyan;linglingdai;`

## 人员输入纠正

当用户输入近似拼写、简写或错误拼写时：
1. 先通过 `people-mapping.md` 做模糊匹配
2. 若能唯一命中，自动纠正并继续
3. 输出时需告知：已将 `<原始输入>` 纠正为 `<标准RTX>`

## 分类ID获取优化

当用户说"放到 440 WOW"或"沿用某分类"时：
1. 优先查询该分类下已存在需求单
2. 直接复用其 `category_id`
3. 不要模糊搜索多个分类后再猜测

## 子单内容模板

创建子单时，description 默认结构：
- 重点特性
- 需求背景
- 需求目的
- 需求内容
- 风险与注意事项

如果用户输入是"1个大点1个单"，应将该大点的所有子条目完整落入 `需求内容`，不要只写一句摘要。

## 操作示例

### 完整创建案例

**场景**：创建一个440WOW分类下的需求单，处理人和后台开发为 linglingdai，负责策划为 tianyishao。

**步骤1：查询分类ID**

```json
{
  "tool_name": "stories_get",
  "tool_args": {
    "workspace_id": "20360302",
    "name": "440",
    "limit": 50,
    "with_v_status": "1"
  }
}
```

> 从结果中找到 440WOW 分类的 `category_id: 1020360302002729717`

**步骤2：创建需求单**

```json
{
  "tool_name": "stories_create",
  "tool_args": {
    "workspace_id": "20360302",
    "name": "【440】【WOW】召回池同质化团竞打压与非团竞扩量",
    "category_id": "1020360302002729717",
    "description": "### 背景\n- 当前全局曝光的作品大多是同质化的团竞内容\n\n### 目的\n- 缩减召回池中同质化团竞作品数量\n- 红海团竞聚焦少量头部图\n- 蓝海非团竞做到百级别优质图推荐",
    "custom_field_49": "纯功能单",
    "custom_field_79": "tianyishao",
    "owner": "linglingdai;",
    "custom_field_78": "linglingdai",
    "custom_field_82": "",
    "creator": "tianyishao"
  }
}
```

> **关键点**：
> - `owner` 值末尾必须带分号：`linglingdai;`
> - `custom_field_82`（前台开发）未指定时填空字符串 `""`
> - **不要传入 `version` 参数**，版本号在标题中体现即可
> 
> 创建成功后输出链接：`https://tapd.woa.com/tapd_fe/20360302/story/detail/1020360302132122346`
