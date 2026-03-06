#!/usr/bin/env python3
"""Web Browser 自动化工具 - 基于 Playwright Python.

统一入口脚本，提供浏览器自动化的全部能力：
- 页面导航与等待
- 元素交互（点击、填表、选择等）
- 内容提取（文本、HTML、属性、截图）
- 页面分析（可交互元素快照）
- Cookie/Storage 管理
- JavaScript 执行

用法:
    python browser.py <command> [args...]

示例:
    python browser.py open https://example.com
    python browser.py snapshot
    python browser.py click "button:text('Submit')"
    python browser.py fill "#email" "user@test.com"
    python browser.py screenshot ./output.png
    python browser.py close
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

# Playwright 延迟导入
_playwright = None
_browser = None
_context = None
_page = None

# 状态文件（用于跨调用保持会话）
STATE_DIR = Path(tempfile.gettempdir()) / "web-browser-skill"
STATE_FILE = STATE_DIR / "session.json"
STORAGE_FILE = STATE_DIR / "storage.json"


def _ensure_state_dir():
    STATE_DIR.mkdir(parents=True, exist_ok=True)


async def _get_playwright():
    """获取 Playwright 实例."""
    global _playwright
    if _playwright is None:
        from playwright.async_api import async_playwright
        _playwright = await async_playwright().start()
    return _playwright


async def _launch_browser(headed: bool = False, **kwargs):
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
        headless=not headed,
        args=launch_args,
    )
    
    # 加载已保存的存储状态
    storage_state = None
    if STORAGE_FILE.exists():
        try:
            storage_state = str(STORAGE_FILE)
        except Exception:
            pass
    
    context_kwargs = {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "viewport": {"width": 1280, "height": 900},
        "locale": "zh-CN",
    }
    if storage_state:
        context_kwargs["storage_state"] = storage_state
    
    _context = await _browser.new_context(**context_kwargs)
    
    # 反检测脚本
    await _context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en-US', 'en'] });
    """)
    
    _page = await _context.new_page()
    return _page


async def _get_page(headed: bool = False) -> Any:
    """获取当前页面，如果没有则启动浏览器."""
    global _page
    if _page is None or _page.is_closed():
        await _launch_browser(headed=headed)
    return _page


async def _save_storage():
    """保存浏览器存储状态（cookie + localStorage）."""
    global _context
    if _context:
        _ensure_state_dir()
        try:
            await _context.storage_state(path=str(STORAGE_FILE))
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════
# 命令实现
# ═══════════════════════════════════════════════════════════

async def cmd_open(url: str, headed: bool = False, wait: str = "domcontentloaded", timeout: int = 30000):
    """打开页面.
    
    Args:
        url: 目标 URL（自动补全 https://）
        headed: 是否显示浏览器窗口
        wait: 等待策略 (domcontentloaded | load | networkidle | commit)
        timeout: 超时时间（毫秒）
    """
    if not url.startswith(("http://", "https://", "file://", "data:", "about:")):
        url = f"https://{url}"
    
    page = await _get_page(headed=headed)
    
    try:
        await page.goto(url, wait_until=wait, timeout=timeout)
    except Exception as e:
        print(f"⚠️  导航警告: {e}", file=sys.stderr)
    
    title = await page.title()
    current_url = page.url
    print(f"✅ 已打开: {current_url}")
    print(f"   标题: {title}")
    
    # 保存会话状态
    _ensure_state_dir()
    STATE_FILE.write_text(json.dumps({"url": current_url, "title": title}))
    await _save_storage()


async def cmd_snapshot(interactive_only: bool = True, selector: str = None, max_depth: int = 5):
    """获取页面可交互元素快照.
    
    类似 agent-browser snapshot -i，返回页面上所有可交互元素及其选择器。
    
    Args:
        interactive_only: 只显示可交互元素（默认 True）
        selector: 限定范围到某个 CSS 选择器
        max_depth: 最大遍历深度
    """
    page = await _get_page()
    
    # 使用 JS 遍历 DOM 获取可交互元素
    js_code = """
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
            // 优先用 id
            if (el.id) return '#' + CSS.escape(el.id);
            // 然后用 name
            if (el.name) return el.tagName.toLowerCase() + '[name="' + el.name + '"]';
            // 然后用 aria-label 或 text
            const label = el.getAttribute('aria-label') || el.getAttribute('placeholder');
            if (label) return el.tagName.toLowerCase() + '[aria-label="' + label + '"]';
            // 最后用 :text() 匹配
            const text = el.textContent?.trim().substring(0, 30);
            if (text && el.children.length === 0) {
                return el.tagName.toLowerCase() + ':has-text("' + text.replace(/"/g, '\\\\"') + '")';
            }
            // 回退到 nth-of-type
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
                    const info = {
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
                    };
                    elements.push(info);
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
    
    result = await page.evaluate(js_code, {
        "interactiveOnly": interactive_only,
        "selector": selector,
        "maxDepth": max_depth,
    })
    
    if "error" in result:
        print(f"❌ {result['error']}")
        return
    
    print(f"📄 {result['title']}")
    print(f"🔗 {result['url']}")
    print(f"Found {result['total']} interactive elements:\n")
    
    for el in result["elements"]:
        ref = el["ref"]
        tag = el["tag"]
        role_str = f" role={el['role']}" if el["role"] else ""
        type_str = f" type={el['type']}" if el["type"] else ""
        
        # 构建描述
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
        
        print(f"  [@{ref}] {tag}{type_str}{role_str} {desc}")
        print(f"          selector: {selector}")
    
    # 返回 JSON 以便程序化处理
    return result


async def cmd_click(selector: str, timeout: int = 5000):
    """点击元素.
    
    Args:
        selector: CSS 选择器、文本匹配（如 text=Submit）或 @ref
    """
    page = await _get_page()
    selector = _resolve_selector(selector)
    
    try:
        await page.click(selector, timeout=timeout)
        print(f"✅ 已点击: {selector}")
    except Exception as e:
        print(f"❌ 点击失败: {e}")
        raise


async def cmd_fill(selector: str, value: str, timeout: int = 5000):
    """填写输入框（先清空再输入）.
    
    Args:
        selector: CSS 选择器
        value: 要填写的文本
    """
    page = await _get_page()
    selector = _resolve_selector(selector)
    
    try:
        await page.fill(selector, value, timeout=timeout)
        print(f"✅ 已填写: {selector} = \"{value[:50]}\"")
    except Exception as e:
        print(f"❌ 填写失败: {e}")
        raise


async def cmd_type(selector: str, text: str, delay: int = 50):
    """逐字符输入文本（不清空）.
    
    Args:
        selector: CSS 选择器
        text: 要输入的文本
        delay: 每个字符之间的延迟（毫秒）
    """
    page = await _get_page()
    selector = _resolve_selector(selector)
    
    await page.type(selector, text, delay=delay)
    print(f"✅ 已输入: {selector} ← \"{text[:50]}\"")


async def cmd_select(selector: str, *values: str):
    """选择下拉框选项.
    
    Args:
        selector: CSS 选择器
        values: 一个或多个选项值
    """
    page = await _get_page()
    selector = _resolve_selector(selector)
    
    await page.select_option(selector, list(values))
    print(f"✅ 已选择: {selector} = {list(values)}")


async def cmd_check(selector: str):
    """勾选复选框."""
    page = await _get_page()
    selector = _resolve_selector(selector)
    await page.check(selector)
    print(f"✅ 已勾选: {selector}")


async def cmd_uncheck(selector: str):
    """取消勾选复选框."""
    page = await _get_page()
    selector = _resolve_selector(selector)
    await page.uncheck(selector)
    print(f"✅ 已取消勾选: {selector}")


async def cmd_hover(selector: str):
    """悬停在元素上."""
    page = await _get_page()
    selector = _resolve_selector(selector)
    await page.hover(selector)
    print(f"✅ 已悬停: {selector}")


async def cmd_press(key: str):
    """按下键盘按键.
    
    Args:
        key: 按键名称，如 Enter, Tab, Escape, Control+a 等
    """
    page = await _get_page()
    await page.keyboard.press(key)
    print(f"✅ 按键: {key}")


async def cmd_scroll(direction: str = "down", amount: int = 500):
    """滚动页面.
    
    Args:
        direction: 方向 (up | down | left | right)
        amount: 滚动距离（像素）
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
    print(f"✅ 滚动: {direction} {amount}px")


async def cmd_wait(target: str = None, timeout: int = 10000):
    """等待.
    
    Args:
        target: 等待目标：
            - 数字 → 等待毫秒
            - CSS 选择器 → 等待元素出现
            - "networkidle" → 等待网络空闲
            - "text:xxx" → 等待文本出现
            - "url:xxx" → 等待 URL 匹配
    """
    page = await _get_page()
    
    if target is None:
        await page.wait_for_timeout(1000)
        print("✅ 等待 1000ms")
        return
    
    # 纯数字 → 等待毫秒
    try:
        ms = int(target)
        await page.wait_for_timeout(ms)
        print(f"✅ 等待 {ms}ms")
        return
    except ValueError:
        pass
    
    if target == "networkidle":
        await page.wait_for_load_state("networkidle", timeout=timeout)
        print("✅ 网络空闲")
    elif target.startswith("text:"):
        text = target[5:]
        await page.wait_for_selector(f"text={text}", timeout=timeout)
        print(f"✅ 文本出现: \"{text}\"")
    elif target.startswith("url:"):
        pattern = target[4:]
        await page.wait_for_url(pattern, timeout=timeout)
        print(f"✅ URL 匹配: {pattern}")
    else:
        # CSS 选择器
        await page.wait_for_selector(target, timeout=timeout)
        print(f"✅ 元素出现: {target}")


async def cmd_get(what: str, selector: str = None):
    """获取页面信息.
    
    Args:
        what: 获取类型 (text | html | value | title | url | attr:xxx | count)
        selector: CSS 选择器（text/html/value/attr/count 需要）
    """
    page = await _get_page()
    
    if what == "title":
        result = await page.title()
    elif what == "url":
        result = page.url
    elif what == "text":
        selector = _resolve_selector(selector or "body")
        el = await page.query_selector(selector)
        result = await el.text_content() if el else ""
    elif what == "html":
        selector = _resolve_selector(selector or "body")
        el = await page.query_selector(selector)
        result = await el.inner_html() if el else ""
    elif what == "value":
        selector = _resolve_selector(selector)
        result = await page.input_value(selector)
    elif what.startswith("attr:"):
        attr_name = what[5:]
        selector = _resolve_selector(selector)
        el = await page.query_selector(selector)
        result = await el.get_attribute(attr_name) if el else None
    elif what == "count":
        selector = _resolve_selector(selector)
        els = await page.query_selector_all(selector)
        result = len(els)
    else:
        print(f"❌ 未知的获取类型: {what}")
        return
    
    print(result)
    return result


async def cmd_screenshot(path: str = None, full_page: bool = False, selector: str = None):
    """截图.
    
    Args:
        path: 保存路径（默认临时目录）
        full_page: 是否截全页
        selector: 只截取某个元素
    """
    page = await _get_page()
    
    if not path:
        _ensure_state_dir()
        path = str(STATE_DIR / "screenshot.png")
    
    # 确保目录存在
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    kwargs = {"path": path, "full_page": full_page}
    
    if selector:
        selector = _resolve_selector(selector)
        el = await page.query_selector(selector)
        if el:
            await el.screenshot(path=path)
        else:
            print(f"❌ 元素未找到: {selector}")
            return
    else:
        await page.screenshot(**kwargs)
    
    print(f"✅ 截图已保存: {path}")
    return path


async def cmd_pdf(path: str = "output.pdf"):
    """保存页面为 PDF."""
    page = await _get_page()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    await page.pdf(path=path)
    print(f"✅ PDF 已保存: {path}")


async def cmd_eval(expression: str):
    """执行 JavaScript 并返回结果.
    
    Args:
        expression: JavaScript 表达式
    """
    page = await _get_page()
    result = await page.evaluate(expression)
    if isinstance(result, (dict, list)):
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)
    return result


async def cmd_cookies(action: str = "get", name: str = None, value: str = None):
    """Cookie 管理.
    
    Args:
        action: 操作 (get | set | clear)
        name: Cookie 名称（set 时需要）
        value: Cookie 值（set 时需要）
    """
    page = await _get_page()
    
    if action == "get":
        cookies = await _context.cookies()
        for c in cookies:
            print(f"  {c['name']}={c['value'][:50]}  (domain={c.get('domain', '')})")
        return cookies
    elif action == "set" and name and value:
        await _context.add_cookies([{
            "name": name,
            "value": value,
            "url": page.url,
        }])
        print(f"✅ Cookie 已设置: {name}={value[:50]}")
    elif action == "clear":
        await _context.clear_cookies()
        print("✅ Cookie 已清空")
    else:
        print("用法: cookies get | cookies set <name> <value> | cookies clear")


async def cmd_state_save(path: str = None):
    """保存浏览器状态（cookies + localStorage）."""
    if not path:
        _ensure_state_dir()
        path = str(STORAGE_FILE)
    
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    await _context.storage_state(path=path)
    print(f"✅ 状态已保存: {path}")


async def cmd_state_load(path: str = None):
    """加载浏览器状态."""
    if not path:
        path = str(STORAGE_FILE)
    
    if not Path(path).exists():
        print(f"❌ 状态文件不存在: {path}")
        return
    
    # 需要重建上下文
    global _context, _page, _browser
    if _context:
        await _context.close()
    if _browser:
        _context = await _browser.new_context(
            storage_state=path,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900},
        )
        _page = await _context.new_page()
    
    print(f"✅ 状态已加载: {path}")


async def cmd_close():
    """关闭浏览器."""
    global _browser, _context, _page, _playwright
    
    # 保存状态
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
    
    print("✅ 浏览器已关闭")


async def cmd_extract(url: str = None, mode: str = "content"):
    """提取页面内容（智能模式）.
    
    调用项目中已有的 WebExtractor，提供高质量的正文提取。
    
    Args:
        url: 目标 URL（不传则用当前页面）
        mode: 提取模式 (content | metadata | full)
    """
    page = await _get_page()
    
    if url:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    
    current_url = page.url
    html = await page.content()
    
    # 尝试调用项目内的 WebExtractor
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))
        from pa.extractors.web import WebExtractor
        
        extractor = WebExtractor()
        result = await extractor.extract(current_url, html=html)
        
        if mode == "metadata":
            print(f"标题: {result.title}")
            print(f"作者: {result.author}")
            print(f"日期: {result.publish_date}")
            print(f"站点: {result.site_name}")
            print(f"类型: {result.site_type}")
        elif mode == "content":
            print(result.content)
        else:  # full
            print(f"# {result.title}\n")
            if result.author:
                print(f"作者: {result.author}")
            if result.publish_date:
                print(f"日期: {result.publish_date}")
            print(f"来源: {result.site_name} ({current_url})\n")
            print("---\n")
            print(result.content)
        
        return result
    except ImportError:
        # 回退到简单提取
        title = await page.title()
        text = await page.inner_text("body")
        print(f"# {title}\n")
        print(f"URL: {current_url}\n")
        print("---\n")
        print(text[:5000])


# ═══════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════

def _resolve_selector(selector: str) -> str:
    """将 @ref 转换为实际选择器（需配合 snapshot 使用）.
    
    支持格式：
    - @e1, @e2 ... → 查找 snapshot 缓存
    - text=xxx → 文本匹配
    - 其他 → 原样返回（CSS 选择器）
    """
    if not selector:
        return selector
    
    # @ref 格式 → 查找缓存
    if selector.startswith("@"):
        ref_file = STATE_DIR / "refs.json"
        if ref_file.exists():
            refs = json.loads(ref_file.read_text())
            ref_key = selector[1:]  # 去掉 @
            if ref_key in refs:
                return refs[ref_key]
        print(f"⚠️  未找到 ref {selector}，请先运行 snapshot 命令", file=sys.stderr)
        return selector[1:]  # 回退
    
    return selector


async def cmd_snapshot_with_refs(**kwargs):
    """snapshot 的增强版本，自动保存 ref → selector 映射."""
    result = await cmd_snapshot(**kwargs)
    
    if result and "elements" in result:
        refs = {}
        for el in result["elements"]:
            refs[el["ref"]] = el["selector"]
        
        _ensure_state_dir()
        refs_file = STATE_DIR / "refs.json"
        refs_file.write_text(json.dumps(refs, ensure_ascii=False))
    
    return result


# ═══════════════════════════════════════════════════════════
# CLI 入口
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Web Browser 自动化工具")
    parser.add_argument("--headed", action="store_true", help="显示浏览器窗口")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # open
    p_open = subparsers.add_parser("open", help="打开页面")
    p_open.add_argument("url", help="目标 URL")
    p_open.add_argument("--wait", default="domcontentloaded", help="等待策略")
    p_open.add_argument("--timeout", type=int, default=30000, help="超时(ms)")
    
    # snapshot
    p_snap = subparsers.add_parser("snapshot", help="页面元素快照")
    p_snap.add_argument("-a", "--all", action="store_true", help="显示所有元素（不只可交互的）")
    p_snap.add_argument("-s", "--selector", help="限定 CSS 选择器范围")
    p_snap.add_argument("-d", "--depth", type=int, default=5, help="最大遍历深度")
    
    # click
    p_click = subparsers.add_parser("click", help="点击元素")
    p_click.add_argument("selector", help="CSS 选择器或 @ref")
    
    # fill
    p_fill = subparsers.add_parser("fill", help="填写输入框")
    p_fill.add_argument("selector", help="CSS 选择器或 @ref")
    p_fill.add_argument("value", help="要填写的文本")
    
    # type
    p_type = subparsers.add_parser("type", help="逐字符输入")
    p_type.add_argument("selector", help="CSS 选择器或 @ref")
    p_type.add_argument("text", help="要输入的文本")
    p_type.add_argument("--delay", type=int, default=50, help="字符间延迟(ms)")
    
    # select
    p_sel = subparsers.add_parser("select", help="选择下拉选项")
    p_sel.add_argument("selector", help="CSS 选择器或 @ref")
    p_sel.add_argument("values", nargs="+", help="选项值")
    
    # check / uncheck
    subparsers.add_parser("check", help="勾选").add_argument("selector")
    subparsers.add_parser("uncheck", help="取消勾选").add_argument("selector")
    subparsers.add_parser("hover", help="悬停").add_argument("selector")
    
    # press
    p_press = subparsers.add_parser("press", help="按键")
    p_press.add_argument("key", help="按键名称")
    
    # scroll
    p_scroll = subparsers.add_parser("scroll", help="滚动页面")
    p_scroll.add_argument("direction", nargs="?", default="down", help="方向")
    p_scroll.add_argument("amount", nargs="?", type=int, default=500, help="距离(px)")
    
    # wait
    p_wait = subparsers.add_parser("wait", help="等待")
    p_wait.add_argument("target", nargs="?", help="等待目标")
    p_wait.add_argument("--timeout", type=int, default=10000, help="超时(ms)")
    
    # get
    p_get = subparsers.add_parser("get", help="获取信息")
    p_get.add_argument("what", help="获取类型 (text|html|value|title|url|attr:xxx|count)")
    p_get.add_argument("selector", nargs="?", help="CSS 选择器")
    
    # screenshot
    p_ss = subparsers.add_parser("screenshot", help="截图")
    p_ss.add_argument("path", nargs="?", help="保存路径")
    p_ss.add_argument("--full", action="store_true", help="全页截图")
    p_ss.add_argument("-s", "--selector", help="截取元素")
    
    # pdf
    p_pdf = subparsers.add_parser("pdf", help="保存为 PDF")
    p_pdf.add_argument("path", nargs="?", default="output.pdf", help="保存路径")
    
    # eval
    p_eval = subparsers.add_parser("eval", help="执行 JavaScript")
    p_eval.add_argument("expression", help="JS 表达式")
    
    # cookies
    p_cookie = subparsers.add_parser("cookies", help="Cookie 管理")
    p_cookie.add_argument("action", nargs="?", default="get", help="操作 (get|set|clear)")
    p_cookie.add_argument("name", nargs="?", help="Cookie 名称")
    p_cookie.add_argument("cookie_value", nargs="?", help="Cookie 值")
    
    # state
    p_state = subparsers.add_parser("state", help="状态管理")
    p_state.add_argument("action", choices=["save", "load"], help="操作")
    p_state.add_argument("path", nargs="?", help="状态文件路径")
    
    # extract
    p_extract = subparsers.add_parser("extract", help="智能提取页面内容")
    p_extract.add_argument("url", nargs="?", help="目标 URL")
    p_extract.add_argument("--mode", default="content", choices=["content", "metadata", "full"], help="提取模式")
    
    # close
    subparsers.add_parser("close", help="关闭浏览器")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 执行命令
    async def run():
        try:
            if args.command == "open":
                await cmd_open(args.url, headed=args.headed, wait=args.wait, timeout=args.timeout)
            elif args.command == "snapshot":
                await cmd_snapshot_with_refs(
                    interactive_only=not args.all,
                    selector=args.selector,
                    max_depth=args.depth,
                )
            elif args.command == "click":
                await cmd_click(args.selector)
            elif args.command == "fill":
                await cmd_fill(args.selector, args.value)
            elif args.command == "type":
                await cmd_type(args.selector, args.text, delay=args.delay)
            elif args.command == "select":
                await cmd_select(args.selector, *args.values)
            elif args.command == "check":
                await cmd_check(args.selector)
            elif args.command == "uncheck":
                await cmd_uncheck(args.selector)
            elif args.command == "hover":
                await cmd_hover(args.selector)
            elif args.command == "press":
                await cmd_press(args.key)
            elif args.command == "scroll":
                await cmd_scroll(args.direction, args.amount)
            elif args.command == "wait":
                await cmd_wait(args.target, timeout=args.timeout)
            elif args.command == "get":
                await cmd_get(args.what, args.selector)
            elif args.command == "screenshot":
                await cmd_screenshot(args.path, full_page=args.full, selector=args.selector)
            elif args.command == "pdf":
                await cmd_pdf(args.path)
            elif args.command == "eval":
                await cmd_eval(args.expression)
            elif args.command == "cookies":
                await cmd_cookies(args.action, args.name, getattr(args, "cookie_value", None))
            elif args.command == "state":
                if args.action == "save":
                    await cmd_state_save(args.path)
                else:
                    await cmd_state_load(args.path)
            elif args.command == "extract":
                await cmd_extract(args.url, mode=args.mode)
            elif args.command == "close":
                await cmd_close()
        except KeyboardInterrupt:
            await cmd_close()
        except Exception as e:
            print(f"❌ 错误: {e}", file=sys.stderr)
            raise
    
    asyncio.run(run())


if __name__ == "__main__":
    main()
