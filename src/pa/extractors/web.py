"""通用 Web 内容提取器.

使用 trafilatura 进行智能正文提取，bs4 解析元数据。
支持自动从 URL 抓取 HTML（无需外部传入）。
三层抓取策略：trafilatura → httpx → Playwright（JS 渲染）。
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from pa.extractors.base import BaseExtractor
from pa.extractors.models import ExtractedContent, ExtractedImage

# 延迟导入可选依赖
trafilatura = None
BeautifulSoup = None
httpx = None


def _get_proxy_for_url(url: str) -> str | None:
    """根据配置判断 URL 是否需要代理，返回代理地址或 None."""
    try:
        from pa.config import load_config
        config = load_config()
        return config.proxy.get_proxy_for_url(url)
    except Exception:
        return None

# 已知需要 JS 渲染才能正常抓取的域名（直接跳到 Playwright）
# 注意：Reddit 不在此列表中，因为我们会自动转换为 old.reddit.com（纯服务端渲染）
_JS_REQUIRED_DOMAINS = {
    "twitter.com",
    "x.com",
    "threads.net",
    "instagram.com",
    "facebook.com",
    "linkedin.com",
    "bloomberg.com",
    "wsj.com",
}

# Reddit 相关域名（会自动转为 old.reddit.com 抓取）
_REDDIT_DOMAINS = {
    "reddit.com",
    "www.reddit.com",
    "new.reddit.com",
    "old.reddit.com",
}


def _import_deps() -> None:
    global trafilatura, BeautifulSoup, httpx
    if trafilatura is None:
        try:
            import trafilatura as _trafilatura
            trafilatura = _trafilatura
        except ImportError:
            pass
    if BeautifulSoup is None:
        try:
            from bs4 import BeautifulSoup as _BS
            BeautifulSoup = _BS
        except ImportError:
            pass
    if httpx is None:
        try:
            import httpx as _httpx
            httpx = _httpx
        except ImportError:
            pass


class WebExtractor(BaseExtractor):
    """通用网页内容提取器."""
    
    name = "web"
    supported_domains = []  # 空列表表示处理所有站点
    
    @staticmethod
    def _needs_js_rendering(url: str) -> bool:
        """判断该 URL 是否需要 JS 渲染."""
        domain = urlparse(url).netloc.lower()
        # 去掉 www. 前缀再匹配
        bare_domain = domain.removeprefix("www.")
        return domain in _JS_REQUIRED_DOMAINS or bare_domain in _JS_REQUIRED_DOMAINS
    
    @staticmethod
    async def _fetch_with_playwright(url: str, timeout: int = 60000) -> str | None:
        """使用 Playwright（无头 Chromium）抓取需要 JS 渲染的页面.
        
        Args:
            url: 网页 URL
            timeout: 页面加载超时时间（毫秒），默认 60 秒
            
        Returns:
            渲染后的 HTML 字符串，失败时返回 None
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            import logging
            logging.getLogger(__name__).warning("Playwright 未安装，跳过 JS 渲染抓取")
            return None
        
        import logging
        logger = logging.getLogger(__name__)
        html = None
        browser = None
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-dev-shm-usage",
                    ],
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 900},
                    locale="en-US",
                    # 伪装更真实的浏览器环境
                    extra_http_headers={
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept-Encoding": "gzip, deflate, br",
                        "DNT": "1",
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "none",
                        "Sec-Fetch-User": "?1",
                        "Upgrade-Insecure-Requests": "1",
                    },
                )
                
                # 注入反检测脚本
                await context.add_init_script("""
                    // 隐藏 webdriver 标记
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    // 伪造 plugins
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                    // 伪造 languages
                    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                """)
                
                page = await context.new_page()
                
                logger.info(f"Playwright: 开始抓取 {url}")
                
                # 使用 domcontentloaded 而非 networkidle（Reddit 等站点有持续网络请求）
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                except Exception as nav_err:
                    logger.warning(f"Playwright: 导航失败 {url}: {nav_err}")
                    await browser.close()
                    return None
                
                # 等待页面主体内容渲染
                await page.wait_for_timeout(5000)
                
                # 尝试等待 Reddit 特定的内容选择器
                domain = urlparse(url).netloc.lower()
                if "reddit.com" in domain:
                    try:
                        # Reddit 的帖子内容通常在这些选择器中
                        await page.wait_for_selector(
                            'shreddit-post, [data-testid="post-container"], .Post, article',
                            timeout=10000,
                        )
                        await page.wait_for_timeout(2000)
                    except Exception:
                        logger.info("Playwright: Reddit 内容选择器等待超时，继续获取页面内容")
                
                # 滚动页面以触发懒加载
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
                await page.wait_for_timeout(1500)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                await page.wait_for_timeout(1500)
                
                html = await page.content()
                
                if html:
                    logger.info(f"Playwright: 成功抓取 {url}，HTML 长度: {len(html)}")
                else:
                    logger.warning(f"Playwright: 页面内容为空 {url}")
                
                await context.close()
                await browser.close()
                browser = None
                
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Playwright 抓取失败 {url}: {type(e).__name__}: {e}")
            if browser:
                try:
                    await browser.close()
                except Exception:
                    pass
        
        return html
    
    @staticmethod
    def _convert_reddit_url(url: str) -> str:
        """将 Reddit URL 转换为 old.reddit.com 版本（纯服务端渲染，不需要 JS）."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        bare_domain = domain.removeprefix("www.")
        
        if bare_domain in _REDDIT_DOMAINS or domain in _REDDIT_DOMAINS:
            # 替换域名为 old.reddit.com
            new_url = url.replace(f"://{parsed.netloc}", "://old.reddit.com", 1)
            return new_url
        return url
    
    @staticmethod
    def _is_reddit_url(url: str) -> bool:
        """判断是否为 Reddit 链接."""
        domain = urlparse(url).netloc.lower()
        bare_domain = domain.removeprefix("www.")
        return domain in _REDDIT_DOMAINS or bare_domain in _REDDIT_DOMAINS
    
    @staticmethod
    async def _fetch_reddit_rss(url: str) -> str | None:
        """通过 Reddit RSS 端点抓取帖子内容（最可靠，因为 RSS 采集已验证可用）.
        
        Reddit 每个帖子 URL 后加 .rss 可获取该帖子及其评论的 RSS feed。
        """
        _import_deps()
        if not httpx:
            return None
        
        import logging
        from xml.etree import ElementTree
        logger = logging.getLogger(__name__)
        
        try:
            # 构建帖子的 RSS URL
            parsed = urlparse(url)
            rss_path = parsed.path.rstrip("/") + ".rss"
            rss_url = f"https://www.reddit.com{rss_path}"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Personal Assistant RSS Reader)",
            }
            proxy = _get_proxy_for_url(rss_url)
            client_kwargs = dict(
                timeout=8,
                follow_redirects=True,
                headers=headers,
            )
            if proxy:
                client_kwargs["proxy"] = proxy
            async with httpx.AsyncClient(**client_kwargs) as client:
                logger.info(f"Reddit RSS: 请求 {rss_url}" + (f" (代理: {proxy})" if proxy else ""))
                response = await client.get(rss_url)
                logger.info(f"Reddit RSS: 响应状态码 {response.status_code}, 内容长度 {len(response.text)}")
                response.raise_for_status()
                rss_text = response.text
            
            if not rss_text or len(rss_text.strip()) < 100:
                return None
            
            # 解析 RSS/Atom feed
            root = ElementTree.fromstring(rss_text)
            ns = "{http://www.w3.org/2005/Atom}"
            
            entries = root.findall(f"{ns}entry")
            if not entries:
                # 尝试 RSS 2.0 格式
                entries = root.findall(".//item")
            
            if not entries:
                logger.warning("Reddit RSS: 没有找到任何 entry")
                return None
            
            # 第一个 entry 通常是帖子本身
            import re
            title = ""
            author = ""
            post_content = ""
            comments_html = []
            
            for i, entry in enumerate(entries):
                entry_title = entry.findtext(f"{ns}title") or entry.findtext("title") or ""
                entry_author = ""
                author_elem = entry.find(f"{ns}author")
                if author_elem is not None:
                    entry_author = author_elem.findtext(f"{ns}name") or ""
                if not entry_author:
                    entry_author = entry.findtext("author") or ""
                
                entry_content = entry.findtext(f"{ns}content") or entry.findtext(f"{ns}summary") or ""
                if not entry_content:
                    entry_content = entry.findtext("description") or ""
                
                # 清理 HTML 实体
                entry_content_clean = re.sub(r"<[^>]+>", " ", entry_content).strip()
                entry_content_clean = re.sub(r"\s+", " ", entry_content_clean)
                
                if i == 0:
                    # 第一个是帖子本身
                    title = entry_title
                    author = entry_author
                    post_content = entry_content  # 保留 HTML
                else:
                    # 后续是评论
                    if entry_content_clean and len(entry_content_clean) > 10:
                        comments_html.append(
                            f'<div class="comment"><p><strong>{entry_author}</strong>:</p>{entry_content}</div>'
                        )
            
            if not title:
                return None
            
            # 提取 subreddit
            subreddit = ""
            link_match = re.search(r"/r/(\w+)/", url)
            if link_match:
                subreddit = link_match.group(1)
            
            # 构建 HTML
            html = f"""<!DOCTYPE html>
<html>
<head><title>{title}</title>
<meta property="og:title" content="{title}">
<meta property="og:site_name" content="Reddit - r/{subreddit}">
<meta name="author" content="{author}">
</head>
<body>
<article>
<h1>{title}</h1>
<p>Posted by <strong>{author}</strong> in <strong>r/{subreddit}</strong></p>
<div class="post-content">{post_content}</div>
<hr>
<h2>Comments ({len(comments_html)})</h2>
{''.join(comments_html[:15])}
</article>
</body>
</html>"""
            
            logger.info(f"Reddit RSS: 成功获取帖子 '{title[:50]}', 含 {len(comments_html)} 条评论")
            return html
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Reddit RSS 失败: {type(e).__name__}: {e}")
            return None
    
    @staticmethod
    async def _fetch_reddit_json(url: str) -> str | None:
        """通过 Reddit JSON API 抓取帖子内容（不需要 JS，速度快）.
        
        Reddit 的每个页面都可以加 .json 后缀获取 JSON 数据。
        """
        _import_deps()
        if not httpx:
            return None
        
        import json
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # 构建 JSON API URL
            parsed = urlparse(url)
            json_path = parsed.path.rstrip("/") + ".json"
            json_url = f"https://www.reddit.com{json_path}"
            
            # 使用真实浏览器 User-Agent，Reddit 会拦截自定义 bot UA
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
            proxy = _get_proxy_for_url(json_url)
            client_kwargs = dict(
                timeout=8,
                follow_redirects=True,
                headers=headers,
            )
            if proxy:
                client_kwargs["proxy"] = proxy
            async with httpx.AsyncClient(**client_kwargs) as client:
                logger.info(f"Reddit JSON API: 请求 {json_url}" + (f" (代理: {proxy})" if proxy else ""))
                response = await client.get(json_url)
                logger.info(f"Reddit JSON API: 响应状态码 {response.status_code}, 内容长度 {len(response.text)}")
                response.raise_for_status()
                data = response.json()
            
            if not data or not isinstance(data, list) or len(data) < 1:
                return None
            
            # 提取帖子内容
            post_data = data[0]["data"]["children"][0]["data"]
            title = post_data.get("title", "")
            selftext = post_data.get("selftext", "") or post_data.get("selftext_html", "")
            author = post_data.get("author", "")
            subreddit = post_data.get("subreddit", "")
            score = post_data.get("score", 0)
            created_utc = post_data.get("created_utc", 0)
            
            # 提取评论
            comments_html = []
            if len(data) > 1:
                for comment_wrapper in data[1]["data"]["children"][:10]:  # 前10条评论
                    if comment_wrapper["kind"] == "t1":
                        c = comment_wrapper["data"]
                        c_author = c.get("author", "[deleted]")
                        c_body = c.get("body", "")
                        c_score = c.get("score", 0)
                        if c_body:
                            comments_html.append(
                                f'<div class="comment"><p><strong>u/{c_author}</strong> ({c_score} points):</p><p>{c_body}</p></div>'
                            )
            
            # 构建伪 HTML 供 trafilatura 提取
            html = f"""<!DOCTYPE html>
<html>
<head><title>{title} : {subreddit}</title>
<meta property="og:title" content="{title}">
<meta property="og:site_name" content="Reddit - r/{subreddit}">
<meta name="author" content="u/{author}">
</head>
<body>
<article>
<h1>{title}</h1>
<p>Posted by <strong>u/{author}</strong> in <strong>r/{subreddit}</strong> | Score: {score}</p>
<div class="post-content">{selftext}</div>
<hr>
<h2>Top Comments</h2>
{''.join(comments_html)}
</article>
</body>
</html>"""
            
            logger.info(f"Reddit JSON API: 成功获取帖子 '{title[:50]}', 含 {len(comments_html)} 条评论")
            return html
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Reddit JSON API 失败: {type(e).__name__}: {e}")
            return None
    
    @staticmethod
    async def fetch_html(url: str) -> str:
        """从 URL 自动抓取 HTML 内容.
        
        抓取策略：
        - Reddit: 优先使用 JSON API → 回退到 old.reddit.com → Playwright
        - 已知 JS 站点: 直接 Playwright → 回退到常规方式
        - 其他站点: trafilatura → httpx → Playwright 兜底
        
        Args:
            url: 网页 URL
            
        Returns:
            HTML 字符串
            
        Raises:
            RuntimeError: 所有抓取方式均失败时抛出
        """
        _import_deps()
        import logging
        logger = logging.getLogger(__name__)
        
        html = None
        is_reddit = WebExtractor._is_reddit_url(url)
        use_js = WebExtractor._needs_js_rendering(url)
        
        # === Reddit 专用策略 ===
        if is_reddit:
            logger.info(f"检测到 Reddit URL，使用 RSS 端点抓取: {url}")
            
            # 只使用 RSS 端点（已验证可用，最快最可靠）
            html = await WebExtractor._fetch_reddit_rss(url)
            if html and len(html.strip()) > 200:
                return html
            
            # RSS 失败时尝试 JSON API（作为唯一的回退）
            html = await WebExtractor._fetch_reddit_json(url)
            if html and len(html.strip()) > 200:
                return html
            
            raise RuntimeError(
                f"无法抓取 Reddit 内容: {url}\n"
                "RSS 端点和 JSON API 均失败。\n"
                "可能原因：网络不通、Reddit 限流或反爬严格。"
            )
        
        # === 已知需要 JS 渲染的站点 ===
        if use_js:
            html = await WebExtractor._fetch_with_playwright(url)
            if html and len(html.strip()) > 200:
                return html
            # Playwright 也失败了，回退到常规方式尝试
            html = None
        
        # === 常规站点：三层策略 ===
        # 第一层：使用 trafilatura 内置下载（它自带重试、编码检测等）
        if trafilatura:
            try:
                downloaded = trafilatura.fetch_url(url)
                if downloaded and len(downloaded.strip()) > 200:
                    html = downloaded
            except Exception:
                pass
        
        # 第二层：回退到 httpx（支持更多自定义 header）
        if not html and httpx:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                }
                proxy = _get_proxy_for_url(url)
                client_kwargs = dict(
                    timeout=30,
                    follow_redirects=True,
                    headers=headers,
                )
                if proxy:
                    client_kwargs["proxy"] = proxy
                async with httpx.AsyncClient(**client_kwargs) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    html = response.text
            except Exception:
                pass
        
        # 第三层：前两层都失败，且不是已知 JS 站点，尝试 Playwright 兜底
        if not html and not use_js:
            html = await WebExtractor._fetch_with_playwright(url)
        
        if not html:
            raise RuntimeError(
                f"无法抓取网页内容: {url}\n"
                "所有抓取方式（trafilatura / httpx / Playwright）均已失败。\n"
                "可能原因：网络不通、反爬严格、或 Playwright 浏览器未安装。\n"
                "请尝试: pip install playwright && playwright install chromium"
            )
        
        return html
    
    async def extract(self, url: str, html: str | None = None) -> ExtractedContent:
        """从 HTML 提取内容. 如果未提供 html，会自动从 url 抓取."""
        _import_deps()
        
        # 如果未提供 HTML，自动抓取
        if not html:
            html = await self.fetch_html(url)
        
        title = ""
        content = ""
        author = ""
        publish_date = ""
        site_name = ""
        cover_image = ""
        
        # 使用 trafilatura 提取正文
        if trafilatura:
            content = trafilatura.extract(
                html,
                include_images=True,
                include_links=True,
                output_format="markdown",
                favor_precision=True,
            ) or ""
            
            # 提取元数据
            metadata = trafilatura.extract_metadata(html)
            if metadata:
                title = metadata.title or ""
                author = metadata.author or ""
                publish_date = metadata.date or ""
                site_name = metadata.sitename or ""
        
        # 使用 bs4 补充元数据
        if BeautifulSoup:
            soup = BeautifulSoup(html, "html.parser")
            
            if not title:
                title = self._extract_title(soup)
            if not author:
                author = self._extract_author(soup)
            if not publish_date:
                publish_date = self._extract_date(soup)
            if not site_name:
                site_name = self._extract_site_name(soup, url)
            cover_image = self._extract_cover_image(soup)
            
            # 如果 trafilatura 失败，尝试简单提取
            if not content:
                content = self._simple_extract(soup)
        
        # 提取图片
        images = self.extract_images_from_content(content)
        
        return ExtractedContent(
            title=title,
            content=content,
            url=url,
            author=author,
            publish_date=publish_date,
            site_name=site_name,
            site_type=self._detect_site_type(url),
            images=images,
            cover_image=cover_image,
            extractor_name=self.name,
        )
    
    def _extract_title(self, soup: Any) -> str:
        """提取标题."""
        # 优先级: og:title > title > h1
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]
        
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text().strip()
        
        h1 = soup.find("h1")
        if h1:
            return h1.get_text().strip()
        
        return ""
    
    def _extract_author(self, soup: Any) -> str:
        """提取作者."""
        selectors = [
            ("meta", {"name": "author"}),
            ("meta", {"property": "article:author"}),
            ("a", {"rel": "author"}),
            ("span", {"class": re.compile(r"author|byline", re.I)}),
        ]
        for tag, attrs in selectors:
            el = soup.find(tag, attrs)
            if el:
                return el.get("content", "") or el.get_text().strip()
        return ""
    
    def _extract_date(self, soup: Any) -> str:
        """提取发布日期."""
        selectors = [
            ("meta", {"property": "article:published_time"}),
            ("meta", {"name": "pubdate"}),
            ("time", {"datetime": True}),
        ]
        for tag, attrs in selectors:
            el = soup.find(tag, attrs)
            if el:
                return el.get("content", "") or el.get("datetime", "")
        return ""
    
    def _extract_site_name(self, soup: Any, url: str) -> str:
        """提取站点名称."""
        og_site = soup.find("meta", property="og:site_name")
        if og_site and og_site.get("content"):
            return og_site["content"]
        return urlparse(url).netloc
    
    def _extract_cover_image(self, soup: Any) -> str:
        """提取封面图."""
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"]
        return ""
    
    def _simple_extract(self, soup: Any) -> str:
        """简单正文提取 (fallback)."""
        # 移除脚本和样式
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        
        # 尝试找 article 或 main
        article = soup.find("article") or soup.find("main")
        if article:
            return article.get_text(separator="\n\n", strip=True)
        
        # 最后用 body
        body = soup.find("body")
        if body:
            return body.get_text(separator="\n\n", strip=True)[:5000]
        
        return ""
    
    def _detect_site_type(self, url: str) -> str:
        """检测站点类型."""
        domain = urlparse(url).netloc.lower()
        
        type_map = {
            "mp.weixin.qq.com": "wechat",
            "weixin.qq.com": "wechat",
            "zhihu.com": "zhihu",
            "juejin.cn": "juejin",
            "juejin.im": "juejin",
            "github.com": "github",
            "medium.com": "medium",
            "twitter.com": "twitter",
            "x.com": "twitter",
        }
        
        for key, site_type in type_map.items():
            if key in domain:
                return site_type
        
        return "articles"
