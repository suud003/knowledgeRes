"""Flomo 笔记采集器."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from pa.collectors.base import BaseCollector


class FlomoCollector(BaseCollector):
    """Flomo HTML 导出文件采集器."""

    def __init__(
        self,
        name: str,
        raw_dir: Path,
        html_file: Path,
    ) -> None:
        super().__init__(name, raw_dir)
        self.html_file = Path(html_file)

    def get_source_type(self) -> str:
        return "flomo"

    def _extract_tag_from_hashtag(self, content: str) -> list[str]:
        """从内容中提取 #标签 格式的标签."""
        # 匹配 #标签 格式 (支持中文、英文、数字、下划线、斜杠)
        # 标签在 HTML 中被转义为 #标签，需要处理两种格式
        tags = []

        # 匹配 #标签 或 #标签/子标签 格式
        # 标签字符包括：中文、英文、数字、下划线、斜杠
        pattern = r'#([\u4e00-\u9fa5\w\/\-\.]+)'
        matches = re.findall(pattern, content)
        for match in matches:
            match = match.strip()
            if match and not match.startswith('#'):
                tags.append(match)

        return tags

    def _html_to_text(self, html_str: str) -> str:
        """将简单的 HTML 转换为纯文本."""
        import html as html_module

        text = html_str

        # 移除 script 和 style
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)

        # 将 <p> 转换为换行
        text = re.sub(r'</p>\s*<p>', '\n\n', text)
        text = re.sub(r'<p[^>]*>', '', text)
        text = re.sub(r'</p>', '', text)

        # 将 <br>, <br/> 转换为换行
        text = re.sub(r'<br\s*/?>', '\n', text)

        # 处理列表
        text = re.sub(r'<li[^>]*>', '- ', text)
        text = re.sub(r'</li>', '\n', text)
        text = re.sub(r'<ol[^>]*>|</ol>|<ul[^>]*>|</ul>', '', text)

        # 移除其他 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)

        # 解码 HTML 实体
        text = html_module.unescape(text)

        # 清理多余空白
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)

        return text.strip()

    def _parse_memo(self, memo_html: str) -> dict[str, Any] | None:
        """解析单条 memo HTML."""
        # 提取时间
        time_match = re.search(r'<div class="time">([^<]+)</div>', memo_html)
        if not time_match:
            return None

        time_str = time_match.group(1).strip()
        try:
            created_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            created_time = datetime.now()

        # 提取内容
        content_match = re.search(
            r'<div class="content">(.*?)</div>\s*(?:<div class="files">|<div class="memo">|</div>\s*</div>\s*<div class="memo">|$)',
            memo_html,
            re.DOTALL
        )
        if not content_match:
            return None

        content_html = content_match.group(1).strip()
        content_text = self._html_to_text(content_html)

        if not content_text:
            return None

        # 提取图片
        images = []
        img_matches = re.findall(r'<img[^>]+src="([^"]+)"', memo_html)
        for img_src in img_matches:
            # 构建相对路径的完整路径
            if not img_src.startswith(('http://', 'https://', '/')):
                # 相对路径，相对于 HTML 文件
                img_path = self.html_file.parent / img_src
                if img_path.exists():
                    images.append(str(img_path.resolve()))
            else:
                images.append(img_src)

        # 从内容中提取标签
        tags = self._extract_tag_from_hashtag(content_text)

        # 生成标题 (取内容的前 30 个字符或第一行)
        first_line = content_text.split('\n')[0].strip()
        title = first_line[:50] + '...' if len(first_line) > 50 else first_line
        if not title:
            title = f"Memo {created_time.strftime('%Y-%m-%d')}"

        return {
            "id": f"flomo_{created_time.strftime('%Y%m%d_%H%M%S')}",
            "source": self.name,
            "source_type": self.get_source_type(),
            "title": title,
            "content": content_text,
            "tags": tags,
            "created_time": created_time.isoformat(),
            "images": images,
            "raw_fields": {
                "html_content": content_html,
                "images": images,
            }
        }

    async def collect(self) -> list[dict[str, Any]]:
        """执行采集."""
        if not self.html_file.exists():
            raise FileNotFoundError(f"Flomo HTML 文件不存在: {self.html_file}")

        # 读取 HTML 文件
        with open(self.html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 提取所有 memo
        memos = re.findall(r'<div class="memo">(.*?)(?=<div class="memo">|</div>\s*</div>\s*</body>|$)', html_content, re.DOTALL)

        records = []
        for memo_html in memos:
            # 添加外层 div 以便正确解析
            full_memo = f'<div class="memo">{memo_html}'
            record = self._parse_memo(full_memo)
            if record:
                records.append(record)

        # 保存原始数据
        self.save_raw(records)

        return records
