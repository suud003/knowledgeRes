#!/usr/bin/env python3
"""测试内容提取器 - 示例脚本."""

from pa.extractors.web import WebContentExtractor

# 示例：替换为你要测试的 URL
url = "https://example.com/article"

extractor = WebContentExtractor()
result = extractor.extract(url)

print(f"标题: {result.title}")
print(f"作者: {result.author}")
print(f"内容长度: {len(result.content)} 字符")
