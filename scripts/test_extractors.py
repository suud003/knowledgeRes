"""测试内容提取器."""

import asyncio
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pa.extractors import ExtractedContent, WebExtractor, ImageHandler
from pa.extractors.sites import WechatExtractor, ZhihuExtractor
from pa.formatters.templates import TemplateRegistry


async def test_extractor_basic():
    """测试基础提取功能."""
    print("=" * 50)
    print("测试 1: 基础提取功能")
    print("=" * 50)
    
    # 模拟简单 HTML
    html = """
    <html>
    <head>
        <title>测试文章标题</title>
        <meta property="og:title" content="测试文章标题">
        <meta property="og:site_name" content="测试网站">
        <meta name="author" content="测试作者">
    </head>
    <body>
        <article>
            <h1>测试文章标题</h1>
            <p>这是第一段正文内容，测试提取功能是否正常工作。</p>
            <p>这是第二段正文内容，包含一些关键信息。</p>
            <img src="https://example.com/image.jpg" alt="测试图片">
        </article>
    </body>
    </html>
    """
    
    extractor = WebExtractor()
    result = await extractor.extract("https://example.com/article", html)
    
    print(f"标题: {result.title}")
    print(f"作者: {result.author}")
    print(f"站点: {result.site_name}")
    print(f"类型: {result.site_type}")
    print(f"图片数: {len(result.images)}")
    print(f"内容长度: {len(result.content)} 字符")
    print()
    
    return result


async def test_templates():
    """测试输出模板."""
    print("=" * 50)
    print("测试 2: 输出模板")
    print("=" * 50)
    
    # 创建测试内容
    content = ExtractedContent(
        title="测试文章",
        content="这是测试内容。\n\n包含多个段落。",
        url="https://mp.weixin.qq.com/s/test",
        author="测试作者",
        site_name="测试公众号",
        site_type="wechat",
        publish_date="2026-03-02",
        tags=["测试", "AI"],
        topic="ai",
    )
    
    # 测试微信模板
    template = TemplateRegistry.get("wechat")
    rendered = template.render(content)
    
    print(f"模板名称: {template.name}")
    print(f"渲染长度: {len(rendered)} 字符")
    print("-" * 30)
    print(rendered[:500])
    print("...")
    print()
    
    return rendered


async def test_image_extract():
    """测试图片提取."""
    print("=" * 50)
    print("测试 3: 图片提取")
    print("=" * 50)
    
    content = """
    # 测试文章
    
    ![图片1](https://example.com/img1.jpg)
    
    一些文字内容
    
    ![图片2](https://example.com/img2.png)
    
    <img src="https://example.com/img3.gif" alt="图片3">
    """
    
    handler = ImageHandler(assets_dir=Path("./test_assets"))
    urls = handler._extract_image_urls(content)
    
    print(f"提取到 {len(urls)} 张图片:")
    for url in urls:
        print(f"  - {url}")
    print()


async def main():
    """运行所有测试."""
    print("\n" + "=" * 50)
    print("内容提取器功能测试")
    print("=" * 50 + "\n")
    
    await test_extractor_basic()
    await test_templates()
    await test_image_extract()
    
    print("=" * 50)
    print("[OK] 所有测试完成!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
