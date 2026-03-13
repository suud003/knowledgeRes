# TAPD 字段映射完整参考

项目：PUBG Mobile（workspace_id: `20360302`）

## 需求（Story）字段映射

### 系统字段

| 字段含义 | API 字段名 | 说明 |
|---------|-----------|------|
| 需求 ID | `id` | 唯一标识，如 `1020360302131247179` |
| 标题 | `name` | 需求标题 |
| 描述 | `description` | 富文本，HTML 格式 |
| 处理人 | `owner` | RTX，末尾带分号，如 `tianyishao;` |
| 创建人 | `creator` | RTX |
| 状态 | `status` | 状态代码，加 `with_v_status=1` 可获取中文 `v_status` |
| 版本 | `version` | 版本号，如 `4.3.0` |
| 分类 | `category_id` | 分类 ID |
| 优先级 | `priority` | 优先级 |
| 模块 | `module` | 模块名 |
| 需求类别 | `workitem_type_id` | 类别 ID，如 `1020360302000028535` |
| 迭代 | `iteration_id` | 迭代 ID |
| 开始时间 | `begin` | 日期 |
| 截止时间 | `due` | 日期 |
| 创建时间 | `created` | 日期时间 |
| 修改时间 | `modified` | 日期时间 |

### 自定义字段

| 字段含义 | API 字段名 | 已知值示例 |
|---------|-----------|-----------|
| 负责策划 | `custom_field_79` | `tianyishao;` |
| 前台开发 | `custom_field_82` | `tianyishao` |
| 后台开发 | `custom_field_78` | `tianyishao` |
| 需求单类型 | `custom_field_49` | `测试单` / `纯功能单` / `纯美术单` / `功能&美术单` / `音效&视频单` / `配置单` |
| 测试人员 | `custom_field_99` | `none;` |
| 是否需要LQA测试 | `custom_field_16` | `否` |
| 转测时间 | `custom_field_38` | `2026-02-09 18:08` |
| 转策划验收时间 | `custom_field_62` | `2026-02-09 18:08` |
| 是否需要美术临时资源 | `custom_field_48` | `不需要` |
| 迭代结束时间 | `custom_field_27` | `2025-12-26` |
| 子需求是否为空 | `custom_field_112` | `是` |
| 品管专项确认 | `custom_field_124` | `适配已确认` |
| 需求新增原因 | `custom_field_145` | `新版本需求提出` |

### 需求状态值映射

| 代码 | 中文名 |
|------|--------|
| `planning` | 规划中 |
| `developing` | 开发中 |
| `for_test` | 转测试 |
| `testing` | 测试中 |
| `resolved` | 已实现 |
| `closed` | 已关闭 |

> 注：实际项目可能有更多自定义状态，可通过 `tapd_fields_summary_get` + `tapd_field_detail_get` 获取完整列表。

---

## 缺陷（Bug）字段映射

### 系统字段

| 字段含义 | API 字段名 | 说明 |
|---------|-----------|------|
| 缺陷 ID | `id` | 唯一标识，如 `1120360302155122519` |
| 标题 | `title` | 缺陷标题 |
| 描述 | `description` | 富文本，HTML 格式 |
| 处理人 | `current_owner` | RTX，末尾带分号 |
| 创建人 | `reporter` | RTX |
| 状态 | `status` | 状态代码，加 `with_v_status=1` 可获取中文 `v_status` |
| 发现版本 | `version_report` | 版本号，如 `4.3.0` |
| 严重程度 | `severity` | `fatal` / `serious` / `normal` / `minor` / `advice` |
| 优先级 | `priority` | 优先级 |
| 模块 | `module` | 模块名 |
| 解决版本 | `version_fix` | 修复的版本号 |
| 迭代 | `iteration_id` | 迭代 ID |
| 截止时间 | `due` | 日期 |
| 创建时间 | `created` | 日期时间 |
| 修改时间 | `modified` | 日期时间 |
| 解决时间 | `resolved` | 日期时间 |
| 关闭时间 | `closed` | 日期时间 |

### 自定义字段

| 字段含义 | API 字段名 | 已知值示例 |
|---------|-----------|-----------|
| 负责策划 | `custom_field_9` | `tianyishao` |
| LQA缺陷类型 | `custom_field_10` | `翻译超框/错行` |
| 测试阶段（新）| `custom_field_18` | `需求验收` |
| 备注 | `custom_field_25` | `提审不等` |
| 测试分组 | `custom_field_30` | `LQA` |
| 测试统计模块 | `custom_field_53` | `LQA专用` |

### 缺陷状态值映射

| 代码 | 中文名 | 说明 |
|------|--------|------|
| `new` | 新建 | 未处理 |
| `in_progress` | 处理中 | 未处理 |
| `open` | 已接受 | 未处理 |
| `resolved` | 已解决 | 未处理（待验证） |
| `reopened` | 重新打开 | 未处理 |
| `audit_reject` | 审核驳回 | 未处理 |
| `verified` | 已验证 | 已关闭 |
| `closed` | 已关闭 | 已关闭 |
| `rejected` | 已拒绝 | 已关闭 |
| `status_2` | 已转需求 | 已关闭（转为需求单处理） |

> ⚠️ **查询未处理 bug 时**：应排除 `verified`、`closed`、`rejected`、`status_2` 等关闭状态。  
> ⚠️ **`status_2`（已转需求）**：表示该 bug 已转为需求单处理，属于关闭状态，无需再作为 bug 跟进。

### 严重程度映射

| 代码 | 中文名 |
|------|--------|
| `fatal` | 致命 |
| `serious` | 严重 |
| `normal` | 一般 |
| `minor` | 轻微 |
| `advice` | 建议 |

---

## 查询参数格式说明

### 多值查询

多个状态值可用 `|` 分隔，如 `status: "new|in_progress|resolved"`。

### 自定义字段查询

自定义字段作为查询条件时，直接使用 `custom_field_XX` 作为参数名传入。

### 分页参数

- `limit`：每页返回数量（默认通常 30）
- `page`：页码

### 排序参数

- `order`：排序字段，如 `created desc`

---

## 工具速查

| 操作 | 工具名 | 关键参数 |
|------|--------|---------|
| 查询需求 | `stories_get` | workspace_id, version, custom_field_79, status |
| 创建需求 | `stories_create` | workspace_id, name, category_id, custom_field_49, custom_field_79, owner, custom_field_82, custom_field_78 |
| 修改需求 | `stories_update` | workspace_id, id, 待更新字段 |
| 统计需求 | `stories_count` | workspace_id, 筛选条件 |
| 查询缺陷 | `bugs_get` | workspace_id, version_report, custom_field_9/current_owner, status |
| 修改缺陷 | `bugs_update` | workspace_id, id, 待更新字段 |
| 统计缺陷 | `bugs_count` | workspace_id, 筛选条件 |
| 需求关联Bug | `get_stories_related_bugs` | workspace_id, story_id |
| Bug描述图片 | `get_workitem_desc_images` | workspace_id, type, entry_id |
| 字段概览 | `tapd_fields_summary_get` | workspace_id, object_type |
| 字段详情 | `tapd_field_detail_get` | workspace_id, object_type, field_label/field_name |
