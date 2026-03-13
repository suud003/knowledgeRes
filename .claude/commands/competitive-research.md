# /competitive-research [target] [mode]

## 功能
执行竞品 AI 落地调研分析。抓取和分析游戏行业竞品（Roblox、元梦之星、蛋仔派对、和平精英绿洲启元）的 AI 应用落地案例，并探索这些 AI 能力在 PUBGM WOW 中的复用性、优化空间和优先级。

## 参数
- `target`（可选）：指定调研的竞品名称，可选值：roblox / yuanmeng / danzai / heping。不指定则调研所有竞品
- `mode`（可选）：执行模式，可选值：full（完整调研） / update（增量更新） / analyze（仅分析已有数据）。默认 full

## 执行步骤

1. **加载参考资料**：读取 `.codebuddy/skills/competitive-ai-research/SKILL.md` 获取完整工作流指引，读取 `.codebuddy/skills/competitive-ai-research/references/` 目录下的参考文件
2. **确定调研范围**：根据 target 参数确定要调研的竞品列表，无参数则调研全部四款竞品
3. **确定执行模式**：根据 mode 参数确定是完整调研、增量更新还是纯分析模式
4. **信息采集**：使用 agent-browser 抓取各竞品的 AI 落地应用相关文章和报道
5. **内容解析与分类**：按 AI 分类框架（AI NPC/AI UGC/AI 辅助/AI 安全 等）对采集内容进行分类
6. **竞品对比分析**：横向对比各竞品的 AI 功能实现，评估技术成熟度和用户价值
7. **PUBGM WOW 适用性评估**：从可复用性、优化空间、优先级三个维度评估哪些 AI 功能适合引入
8. **生成报告**：输出结构化的竞品调研分析报告
9. **双写保存**：同时保存到本地 `raw data/competitive_research/reports/` 目录和 iWiki 工作目录

## 使用示例

```
/competitive-research                          → 完整调研所有竞品
/competitive-research roblox                   → 只调研 Roblox
/competitive-research danzai update            → 增量更新蛋仔派对的调研数据
/competitive-research --target heping          → 只调研和平精英绿洲启元
/competitive-research --mode analyze           → 仅基于已有数据做分析
```

## 输出格式示例

```
🔍 竞品 AI 落地调研报告 - 2026年3月6日

## 调研范围
Roblox / 元梦之星 / 蛋仔派对 / 和平精英（绿洲启元）

## 各竞品 AI 功能总览

### 【Roblox】
- 🤖 AI NPC：基于 LLM 的 NPC 对话系统...
- 🎨 AI UGC：AI 辅助地图/模型生成...

### 【元梦之星】
- 🎨 AI UGC：AI 生成地图皮肤...

## PUBGM WOW 适用性评估

### 可直接复用 ✅
| 功能 | 来源竞品 | 复用难度 | 预期价值 |
|------|----------|----------|----------|
| ... | ... | ... | ... |

### 可优化引入 🔧
...

### 建议优先级排序 📊
...
```
