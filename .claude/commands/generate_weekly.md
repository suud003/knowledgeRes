# /generate_weekly [YYYY-WNN | YYYY-MM-DD~YYYY-MM-DD]

## 功能
生成周报。自动读取本周（或指定周次/日期范围）的所有打字数据，逐日解析后汇总，智能合并重复内容，按项目分类生成格式化周报并发布到 iWiki。

## 参数
- `YYYY-WNN`（可选）：指定 ISO 周次，如 `2026-W10`
- `YYYY-MM-DD~YYYY-MM-DD`（可选）：指定起止日期范围
- 不传参数则默认生成本周的周报

## 执行步骤

1. **加载参考资料**：读取 `.codebuddy/skills/daily-weekly-report/SKILL.md` 获取完整工作流指引
2. **确定日期范围**：
   - 无参数：本周一到今天
   - `YYYY-WNN`：该周一到周日
   - `起始~结束`：使用指定日期范围
3. **批量读取打字数据**：从 `raw data/type_record/` 目录读取日期范围内所有 `keyboard_{日期}.txt` 文件
4. **加载解析器**：读取 `.codebuddy/skills/type-record-parser/SKILL.md` 和 `.codebuddy/skills/type-record-parser/references/pinyin-mapping.md` 获取解析规则
5. **逐日解析**：对每个文件按照 type-record-parser 规则还原为可读中文
6. **合并汇总**：合并重复内容，提炼核心进展，识别跨天持续性工作
7. **生成周报**：使用周报模板生成格式化文档（含进度表格）
8. **用户预览确认**：展示周报预览，等待用户确认或修改
9. **发布到 iWiki**：确认后发布到 iWiki 日报文件夹

## 使用示例

```
/generate_weekly                        → 生成本周的周报
/generate_weekly 2026-W10               → 生成2026年第10周的周报
/generate_weekly 2026-03-03~2026-03-07  → 生成3月3日到3月7日的周报
```

## 输出格式示例

```
📊 周报 - 2026年3月3日 ~ 3月7日

## 本周概要
简要总结本周整体工作进展

## 工作进展

### 【项目A】
| 工作内容 | 状态 | 进度 | 备注 |
|---------|------|------|------|
| 功能开发XXX | 已完成 | 100% | 已合入主干 |

## 问题与风险
- 问题描述

## 下周计划
- 计划内容
```
