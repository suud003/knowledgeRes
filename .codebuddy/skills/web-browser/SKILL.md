---
name: web-browser
description: "基于 Playwright Python 的浏览器自动化工具。已注册为 MCP 工具，可通过 use_mcp_tool 直接调用，无需 CLI 或 Bash。用于网页浏览、表单填写、截图、内容提取、页面交互等任务。适用场景：用户需要浏览网页、与网页交互、填写表单、截图、测试 Web 应用或从网页提取信息。"
---

# Web Browser 自动化（MCP 工具集）

## 概述

浏览器能力已注册为 `personal-assistant` MCP Server 的工具，可通过 `use_mcp_tool` 直接调用。
浏览器实例在 MCP 进程中**持久化**，跨调用自动复用（无需每次重启）。

## 核心工作流

1. **导航**: `browser_navigate` → 打开页面
2. **快照**: `browser_snapshot` → 获取可交互元素及其 @ref
3. **交互**: 使用 @ref 进行 `browser_click` / `browser_fill` 等操作
4. **重新快照**: 页面变化后重新 `browser_snapshot` 获取最新元素
5. **关闭**: `browser_close`（可选，下次调用自动重启）

## MCP 工具列表

> 所有工具通过 `use_mcp_tool(serverName="personal-assistant", toolName="browser_xxx")` 调用。

### 导航

| 工具 | 说明 | 关键参数 |
|------|------|----------|
| `browser_navigate` | 打开/导航到 URL | `url`(必填), `wait`="domcontentloaded", `timeout`=30000 |
| `browser_close` | 关闭浏览器 | 无 |

### 快照

| 工具 | 说明 | 关键参数 |
|------|------|----------|
| `browser_snapshot` | 获取可交互元素快照 | `interactive_only`=true, `selector`=null, `max_depth`=5 |

快照返回每个元素的 `@ref`（如 `@e1`, `@e2`）和 `selector`，后续操作可直接使用 `@e1` 作为 selector。

### 交互

| 工具 | 说明 | 关键参数 |
|------|------|----------|
| `browser_click` | 点击元素 | `selector`(必填), `timeout`=5000 |
| `browser_fill` | 清空并填写输入框 | `selector`(必填), `value`(必填) |
| `browser_type` | 逐字符输入（不清空） | `selector`(必填), `text`(必填), `delay`=50 |
| `browser_select` | 选择下拉选项 | `selector`(必填), `values`(逗号分隔) |
| `browser_scroll` | 滚动页面 | `direction`="down", `amount`=500 |
| `browser_press` | 按键 | `key`(如 "Enter", "Tab") |

### 获取信息

| 工具 | 说明 | 关键参数 |
|------|------|----------|
| `browser_get` | 获取页面信息 | `what`(必填): title/url/text/html/value/attr:xxx/count, `selector` |
| `browser_eval` | 执行 JavaScript | `expression`(必填) |

### 等待

| 工具 | 说明 | 关键参数 |
|------|------|----------|
| `browser_wait` | 等待页面状态 | `target`: 毫秒数/CSS选择器/"networkidle"/"text:xxx"/"url:xxx" |

### 截图与提取

| 工具 | 说明 | 关键参数 |
|------|------|----------|
| `browser_screenshot` | 截图 | `path`, `full_page`=false, `selector` |
| `browser_extract` | 智能正文提取 | `url`(可选), `mode`="content"/"metadata"/"full" |

## 选择器语法

```
# CSS 选择器
"#login-btn"
".submit-form input[type=email]"

# 文本匹配
"text=Sign In"

# @ref（需先运行 browser_snapshot）
"@e1"
"@e3"
```

## 示例：表单提交

```
1. browser_navigate(url="https://example.com/form")
2. browser_snapshot()
   → 输出: [@e1] input type=email, [@e2] input type=password, [@e3] button "Submit"
3. browser_fill(selector="@e1", value="user@example.com")
4. browser_fill(selector="@e2", value="password123")
5. browser_click(selector="@e3")
6. browser_wait(target="networkidle")
7. browser_screenshot(path="./form-result.png")
```

## 示例：内容抓取

```
1. browser_navigate(url="https://blog.example.com/article")
2. browser_extract(mode="full")
   → 返回完整的正文 + 元数据
```

## 技术说明

- **持久化**: 浏览器实例在 MCP 进程生命周期内持久化，跨调用复用 Cookie 和登录状态
- **反检测**: 自动隐藏 webdriver 标识，模拟真实用户 UA
- **智能提取**: `browser_extract` 集成项目 `WebExtractor`（trafilatura + bs4）
- **状态保存**: Cookie/Storage 自动保存到临时目录，MCP 重启后可恢复
- **依赖**: `playwright` 包 + Chromium（需 `playwright install chromium`）
- **源码**: MCP 工具定义在 `src/pa/browser_tools.py`，在 `mcp_server.py` 的 `main()` 中注册
