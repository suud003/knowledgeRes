"""浏览器自动化 MCP 工具集.

将 Playwright 浏览器能力注册为 MCP 工具，实现：
- 浏览器实例在 MCP 进程中持久化（跨调用复用）
- 无需 CLI、Bash 或外部进程
- 通过 use_mcp_tool 直接调用

使用方式：在 mcp_server.py 中调用 register_browser_tools(mcp) 注册所有工具。
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

# Playwright 延迟导入 - 实例在模块级持久化
_playwright = None
_browser = None
_context = None
_page = None

# 状态与缓存
STATE_DIR = Path(tempfile.gettempdir()) / "mcp-browser"
STORAGE_FILE = STATE_DIR / "storage.json"
REFS_FILE = STATE_DIR / "refs.json"


def _ensure_state_dir():
    STATE_DIR.mkdir(parents=True, exist_ok=True)


async def _get_playwright():
    global _playwright
    if _playwright is None:
        from playwright.async_api import async_playwright
        _playwright = await async_playwright().start()
    return _playwright


async def _launch_browser(headless: bool = True):
    """启动浏览器并创建上下文."""
    global _browser, _context, _page

    pw = await _get_playwright()

    launch_args = [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
    ]

    _browser = await pw.chromium.launch(
        headless=headless,
        args=launch_args,
    )

    # 加载已保存的存储状态
    storage_state = None
    if STORAGE_FILE.exists():
        try:
            storage_state = str(STORAGE_FILE)
        except Exception:
            storage_state = None

    _context = await _browser.new_context(
        storage_state=storage_state,
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.6778.139 Safari/537.36"
        ),
        viewport={"width": 1280, "height": 900},
        locale="zh-CN",
    )

    # 注入反检测脚本
    await _context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en-US', 'en'] });
    """)

    _page = await _context.new_page()
    return _page


async def _get_page(headless: bool = True):
    """获取当前页面，如果没有则启动浏览器."""
    global _page
    if _page is None or _page.is_closed():
        await _launch_browser(headless=headless)
    return _page


async def _save_storage():
    """保存浏览器存储状态."""
    global _context
    if _context:
        _ensure_state_dir()
        try:
            await _context.storage_state(path=str(STORAGE_FILE))
        except Exception:
            pass


def _resolve_selector(selector: str) -> str:
    """将 @ref 转换为实际选择器."""
    if not selector:
        return selector
    if selector.startswith("@"):
        if REFS_FILE.exists():
            refs = json.loads(REFS_FILE.read_text())
            ref_key = selector[1:]
            if ref_key in refs:
                return refs[ref_key]
        return selector[1:]
    return selector


# ═══════════════════════════════════════════════════════════
# 快照用的 JavaScript（页面元素扫描）
# ═══════════════════════════════════════════════════════════

_SNAPSHOT_JS = """
(options) => {
    const { interactiveOnly, selector, maxDepth } = options;
    const root = selector ? document.querySelector(selector) : document.body;
    if (!root) return { error: 'Selector not found: ' + selector };

    const interactiveTags = new Set([
        'A', 'BUTTON', 'INPUT', 'TEXTAREA', 'SELECT', 'DETAILS', 'SUMMARY'
    ]);
    const interactiveRoles = new Set([
        'button', 'link', 'textbox', 'checkbox', 'radio', 'combobox',
        'listbox', 'menuitem', 'tab', 'switch', 'searchbox', 'slider',
        'spinbutton', 'option', 'menuitemcheckbox', 'menuitemradio'
    ]);

    const elements = [];
    let index = 1;

    function getSelector(el) {
        if (el.id) return '#' + CSS.escape(el.id);
        if (el.name) return el.tagName.toLowerCase() + '[name="' + el.name + '"]';
        const label = el.getAttribute('aria-label') || el.getAttribute('placeholder');
        if (label) return el.tagName.toLowerCase() + '[aria-label="' + label + '"]';
        const text = el.textContent?.trim().substring(0, 30);
        if (text && el.children.length === 0) {
            return el.tagName.toLowerCase() + ':has-text("' + text.replace(/"/g, '\\\\"') + '")';
        }
        const parent = el.parentElement;
        if (!parent) return el.tagName.toLowerCase();
        const siblings = Array.from(parent.children).filter(c => c.tagName === el.tagName);
        const idx = siblings.indexOf(el) + 1;
        return el.tagName.toLowerCase() + ':nth-of-type(' + idx + ')';
    }

    function walk(node, depth) {
        if (depth > maxDepth) return;
        if (node.nodeType !== 1) return;

        const tag = node.tagName;
        const role = node.getAttribute('role');
        const tabIndex = node.getAttribute('tabindex');
        const isContentEditable = node.isContentEditable;
        const isClickHandler = node.onclick !== null;

        const isInteractive = interactiveTags.has(tag) ||
            interactiveRoles.has(role) ||
            tabIndex !== null ||
            isContentEditable ||
            isClickHandler;

        if (!interactiveOnly || isInteractive) {
            const rect = node.getBoundingClientRect();
            const isVisible = rect.width > 0 && rect.height > 0 &&
                getComputedStyle(node).visibility !== 'hidden' &&
                getComputedStyle(node).display !== 'none';

            if (isVisible) {
                elements.push({
                    ref: 'e' + index,
                    tag: tag.toLowerCase(),
                    type: node.type || '',
                    role: role || '',
                    text: (node.textContent || '').trim().substring(0, 80),
                    value: node.value || '',
                    placeholder: node.placeholder || '',
                    name: node.name || '',
                    href: node.href || '',
                    ariaLabel: node.getAttribute('aria-label') || '',
                    selector: getSelector(node),
                    checked: node.checked || false,
                    disabled: node.disabled || false,
                });
                index++;
            }
        }

        for (const child of node.children) {
            walk(child, depth + 1);
        }
    }

    walk(root, 0);
    return { elements, total: elements.length, url: location.href, title: document.title };
}
"""


def _format_snapshot(result: dict) -> str:
    """将快照结果格式化为可读文本."""
    lines = [
        f"📄 {result['title']}",
        f"🔗 {result['url']}",
        f"找到 {result['total']} 个可交互元素:\n",
    ]

    for el in result["elements"]:
        ref = el["ref"]
        tag = el["tag"]
        role_str = f" role={el['role']}" if el["role"] else ""
        type_str = f" type={el['type']}" if el["type"] else ""

        desc_parts = []
        if el["ariaLabel"]:
            desc_parts.append(f'"{el["ariaLabel"]}"')
        elif el["placeholder"]:
            desc_parts.append(f'placeholder="{el["placeholder"]}"')
        elif el["text"] and len(el["text"]) < 50:
            desc_parts.append(f'"{el["text"]}"')

        if el["value"]:
            desc_parts.append(f'value="{el["value"][:30]}"')
        if el["href"]:
            desc_parts.append(f'href="{el["href"][:60]}"')
        if el["checked"]:
            desc_parts.append("☑ checked")
        if el["disabled"]:
            desc_parts.append("🚫 disabled")

        desc = " ".join(desc_parts)
        selector = el["selector"]

        lines.append(f"  [@{ref}] {tag}{type_str}{role_str} {desc}")
        lines.append(f"          selector: {selector}")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# MCP 工具注册
# ═══════════════════════════════════════════════════════════

def register_browser_tools(mcp):
    """将浏览器工具注册到 MCP Server 实例."""

    @mcp.tool()
    async def browser_navigate(url: str, wait: str = "domcontentloaded", timeout: int = 30000) -> str:
        """打开或导航到指定 URL.

        Args:
            url: 目标 URL（自动补全 https://）
            wait: 等待策略 (domcontentloaded | load | networkidle | commit)
            timeout: 超时时间（毫秒，默认 30000）

        Returns:
            页面标题和 URL
        """
        if not url.startswith(("http://", "https://", "file://", "data:", "about:")):
            url = f"https://{url}"

        page = await _get_page()

        try:
            await page.goto(url, wait_until=wait, timeout=timeout)
        except Exception as e:
            return f"⚠️ 导航警告（页面可能已部分加载）: {e}"

        title = await page.title()
        current_url = page.url

        # 保存会话状态
        _ensure_state_dir()
        (STATE_DIR / "session.json").write_text(
            json.dumps({"url": current_url, "title": title})
        )
        await _save_storage()

        return f"✅ 已打开: {current_url}\n标题: {title}"

    @mcp.tool()
    async def browser_snapshot(
        interactive_only: bool = True,
        selector: str = None,
        max_depth: int = 5,
    ) -> str:
        """获取页面可交互元素快照，返回所有可交互元素及其 @ref 和 selector.

        每个元素有一个 @ref（如 @e1, @e2），可直接用于 browser_click/browser_fill 等工具的 selector 参数。

        Args:
            interactive_only: 只显示可交互元素（默认 True）
            selector: 限定范围的 CSS 选择器
            max_depth: 最大遍历深度

        Returns:
            格式化的元素列表
        """
        page = await _get_page()

        result = await page.evaluate(_SNAPSHOT_JS, {
            "interactiveOnly": interactive_only,
            "selector": selector,
            "maxDepth": max_depth,
        })

        if "error" in result:
            return f"❌ {result['error']}"

        # 保存 ref → selector 映射
        if result.get("elements"):
            refs = {el["ref"]: el["selector"] for el in result["elements"]}
            _ensure_state_dir()
            REFS_FILE.write_text(json.dumps(refs, ensure_ascii=False))

        return _format_snapshot(result)

    @mcp.tool()
    async def browser_click(selector: str, timeout: int = 5000) -> str:
        """点击页面元素.

        Args:
            selector: CSS 选择器、text=xxx 文本匹配、或 @ref（来自 browser_snapshot）
            timeout: 超时毫秒

        Returns:
            操作结果
        """
        page = await _get_page()
        resolved = _resolve_selector(selector)

        try:
            await page.click(resolved, timeout=timeout)
            await _save_storage()
            return f"✅ 已点击: {selector}"
        except Exception as e:
            return f"❌ 点击失败: {e}"

    @mcp.tool()
    async def browser_fill(selector: str, value: str, timeout: int = 5000) -> str:
        """填写输入框（先清空再输入）.

        Args:
            selector: CSS 选择器或 @ref
            value: 要填写的文本
            timeout: 超时毫秒

        Returns:
            操作结果
        """
        page = await _get_page()
        resolved = _resolve_selector(selector)

        try:
            await page.fill(resolved, value, timeout=timeout)
            return f'✅ 已填写: {selector} = "{value[:50]}"'
        except Exception as e:
            return f"❌ 填写失败: {e}"

    @mcp.tool()
    async def browser_type(selector: str, text: str, delay: int = 50) -> str:
        """逐字符输入文本（不清空，模拟真实打字）.

        Args:
            selector: CSS 选择器或 @ref
            text: 要输入的文本
            delay: 每个字符之间的延迟（毫秒）

        Returns:
            操作结果
        """
        page = await _get_page()
        resolved = _resolve_selector(selector)

        await page.type(resolved, text, delay=delay)
        return f'✅ 已输入: {selector} ← "{text[:50]}"'

    @mcp.tool()
    async def browser_select(selector: str, values: str) -> str:
        """选择下拉框选项.

        Args:
            selector: CSS 选择器或 @ref
            values: 选项值（多个用英文逗号分隔）

        Returns:
            操作结果
        """
        page = await _get_page()
        resolved = _resolve_selector(selector)

        value_list = [v.strip() for v in values.split(",")]
        await page.select_option(resolved, value_list)
        return f"✅ 已选择: {selector} = {value_list}"

    @mcp.tool()
    async def browser_scroll(direction: str = "down", amount: int = 500) -> str:
        """滚动页面.

        Args:
            direction: 方向 (up | down | left | right)
            amount: 滚动距离（像素，默认 500）

        Returns:
            操作结果
        """
        page = await _get_page()

        delta_map = {
            "down": (0, amount),
            "up": (0, -amount),
            "right": (amount, 0),
            "left": (-amount, 0),
        }
        dx, dy = delta_map.get(direction, (0, amount))
        await page.mouse.wheel(dx, dy)
        return f"✅ 滚动: {direction} {amount}px"

    @mcp.tool()
    async def browser_press(key: str) -> str:
        """按下键盘按键.

        Args:
            key: 按键名称，如 Enter, Tab, Escape, Control+a, ArrowDown 等

        Returns:
            操作结果
        """
        page = await _get_page()
        await page.keyboard.press(key)
        return f"✅ 按键: {key}"

    @mcp.tool()
    async def browser_wait(target: str = None, timeout: int = 10000) -> str:
        """等待页面状态.

        Args:
            target: 等待目标：
                - 数字（如 "2000"）→ 等待毫秒
                - CSS 选择器 → 等待元素出现
                - "networkidle" → 等待网络空闲
                - "text:xxx" → 等待文本出现
                - "url:xxx" → 等待 URL 匹配
                - 不传 → 等待 1 秒
            timeout: 超时毫秒

        Returns:
            操作结果
        """
        page = await _get_page()

        if target is None:
            await page.wait_for_timeout(1000)
            return "✅ 等待 1000ms"

        # 纯数字
        try:
            ms = int(target)
            await page.wait_for_timeout(ms)
            return f"✅ 等待 {ms}ms"
        except ValueError:
            pass

        if target == "networkidle":
            await page.wait_for_load_state("networkidle", timeout=timeout)
            return "✅ 网络空闲"
        elif target.startswith("text:"):
            text = target[5:]
            await page.wait_for_selector(f"text={text}", timeout=timeout)
            return f'✅ 文本出现: "{text}"'
        elif target.startswith("url:"):
            pattern = target[4:]
            await page.wait_for_url(pattern, timeout=timeout)
            return f"✅ URL 匹配: {pattern}"
        else:
            await page.wait_for_selector(target, timeout=timeout)
            return f"✅ 元素出现: {target}"

    @mcp.tool()
    async def browser_get(what: str, selector: str = None) -> str:
        """获取页面信息.

        Args:
            what: 获取类型：
                - "title" → 页面标题
                - "url" → 当前 URL
                - "text" → 元素文本内容（需 selector）
                - "html" → 元素 HTML（需 selector）
                - "value" → 输入框值（需 selector）
                - "attr:xxx" → 元素属性（需 selector）
                - "count" → 匹配元素数量（需 selector）
            selector: CSS 选择器或 @ref（title/url 不需要）

        Returns:
            获取到的信息
        """
        page = await _get_page()

        if what == "title":
            return await page.title()
        elif what == "url":
            return page.url
        elif what == "text":
            resolved = _resolve_selector(selector or "body")
            el = await page.query_selector(resolved)
            return (await el.text_content() if el else "") or ""
        elif what == "html":
            resolved = _resolve_selector(selector or "body")
            el = await page.query_selector(resolved)
            return (await el.inner_html() if el else "") or ""
        elif what == "value":
            resolved = _resolve_selector(selector)
            return await page.input_value(resolved)
        elif what.startswith("attr:"):
            attr_name = what[5:]
            resolved = _resolve_selector(selector)
            el = await page.query_selector(resolved)
            return (await el.get_attribute(attr_name) if el else None) or ""
        elif what == "count":
            resolved = _resolve_selector(selector)
            els = await page.query_selector_all(resolved)
            return str(len(els))
        else:
            return f"❌ 未知的获取类型: {what}。支持: title, url, text, html, value, attr:xxx, count"

    @mcp.tool()
    async def browser_screenshot(
        path: str = None,
        full_page: bool = False,
        selector: str = None,
    ) -> str:
        """截取页面或元素的截图.

        Args:
            path: 保存路径（不传则保存到临时目录）
            full_page: 是否截取全页（默认 False）
            selector: 只截取某个元素（CSS 选择器或 @ref）

        Returns:
            截图保存路径
        """
        page = await _get_page()

        if not path:
            _ensure_state_dir()
            path = str(STATE_DIR / "screenshot.png")

        Path(path).parent.mkdir(parents=True, exist_ok=True)

        if selector:
            resolved = _resolve_selector(selector)
            el = await page.query_selector(resolved)
            if el:
                await el.screenshot(path=path)
            else:
                return f"❌ 元素未找到: {selector}"
        else:
            await page.screenshot(path=path, full_page=full_page)

        return f"✅ 截图已保存: {path}"

    @mcp.tool()
    async def browser_eval(expression: str) -> str:
        """在当前页面执行 JavaScript 表达式并返回结果.

        Args:
            expression: JavaScript 表达式

        Returns:
            执行结果（JSON 格式或字符串）
        """
        page = await _get_page()
        result = await page.evaluate(expression)
        if isinstance(result, (dict, list)):
            return json.dumps(result, ensure_ascii=False, indent=2)
        return str(result) if result is not None else ""

    @mcp.tool()
    async def browser_extract(url: str = None, mode: str = "content") -> str:
        """智能提取页面正文内容.

        使用项目内置的 WebExtractor 进行高质量正文提取，适合文章/新闻等内容型页面。

        Args:
            url: 目标 URL（不传则提取当前页面）
            mode: 提取模式：
                - "content" → 只返回正文
                - "metadata" → 只返回元数据（标题、作者、日期等）
                - "full" → 正文 + 元数据

        Returns:
            提取的内容
        """
        page = await _get_page()

        if url:
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        current_url = page.url
        html = await page.content()

        # 尝试调用项目内的 WebExtractor
        try:
            from pa.extractors.web import WebExtractor

            extractor = WebExtractor()
            result = await extractor.extract(current_url, html=html)

            if mode == "metadata":
                parts = [
                    f"标题: {result.title}",
                    f"作者: {result.author}",
                    f"日期: {result.publish_date}",
                    f"站点: {result.site_name}",
                    f"类型: {result.site_type}",
                ]
                return "\n".join(parts)
            elif mode == "content":
                return result.content
            else:  # full
                parts = [
                    f"# {result.title}\n",
                ]
                if result.author:
                    parts.append(f"作者: {result.author}")
                if result.publish_date:
                    parts.append(f"日期: {result.publish_date}")
                parts.append(f"来源: {result.site_name} ({current_url})\n")
                parts.append("---\n")
                parts.append(result.content)
                return "\n".join(parts)
        except ImportError:
            # 回退到简单提取
            title = await page.title()
            text = await page.inner_text("body")
            return f"# {title}\n\nURL: {current_url}\n\n---\n\n{text[:5000]}"

    @mcp.tool()
    async def browser_close() -> str:
        """关闭浏览器，释放资源.

        调用后浏览器实例被销毁，下次使用任何 browser_* 工具时会自动重新启动。

        Returns:
            操作结果
        """
        global _browser, _context, _page, _playwright

        await _save_storage()

        if _page and not _page.is_closed():
            await _page.close()
        if _context:
            await _context.close()
        if _browser:
            await _browser.close()
        if _playwright:
            await _playwright.stop()

        _page = None
        _context = None
        _browser = None
        _playwright = None

        return "✅ 浏览器已关闭"
