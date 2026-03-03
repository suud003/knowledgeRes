"""多类型输出模板.

为不同来源类型的内容提供定制化的输出格式。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pa.extractors.models import ExtractedContent


class BaseTemplate(ABC):
    """模板基类."""
    
    name: str = "base"
    
    @abstractmethod
    def render(self, content: "ExtractedContent", **kwargs: Any) -> str:
        """渲染内容为 Markdown 格式."""
        pass
    
    def _format_frontmatter(self, data: dict[str, Any]) -> str:
        """生成 YAML Frontmatter."""
        lines = ["---"]
        for key, value in data.items():
            if value:
                if isinstance(value, list):
                    value_str = ", ".join([f'"{v}"' for v in value])
                    lines.append(f"{key}: [{value_str}]")
                elif isinstance(value, str) and (" " in value or ":" in value):
                    lines.append(f'{key}: "{value}"')
                else:
                    lines.append(f"{key}: {value}")
        lines.append("---")
        return "\n".join(lines)


class WechatTemplate(BaseTemplate):
    """微信公众号文章模板."""
    
    name = "wechat"
    
    def render(self, content: "ExtractedContent", **kwargs: Any) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        frontmatter = self._format_frontmatter({
            "created": now,
            "modified": now,
            "tags": self._build_tags(content),
            "source-type": "collected",
            "source": "wechat",
            "url": content.url,
            "author": content.author,
            "account": content.site_name,  # 公众号名称
            "publish_date": content.publish_date,
            "status": "collected",
        })
        
        lines = [
            frontmatter,
            "",
            f"# {content.title}",
            "",
            f"> **公众号**: {content.site_name}",
        ]
        
        if content.author and content.author != content.site_name:
            lines.append(f"> **作者**: {content.author}")
        if content.publish_date:
            lines.append(f"> **发布时间**: {content.publish_date}")
        
        lines.append("")
        
        if content.summary:
            lines.extend(["## 摘要", "", content.summary, ""])
        
        lines.extend(["## 正文", "", content.content, ""])
        
        lines.extend([
            "## 来源",
            "",
            f"- **原文**: [{content.title}]({content.url})",
            f"- **公众号**: {content.site_name}",
            "",
            "---",
            "",
        ])
        
        return "\n".join(lines)
    
    def _build_tags(self, content: "ExtractedContent") -> list[str]:
        tags = ["collected", "wechat"]
        if content.topic:
            tags.append(content.topic)
        tags.extend(content.tags)
        return list(set(tags))


class ZhihuTemplate(BaseTemplate):
    """知乎文章/回答模板."""
    
    name = "zhihu"
    
    def render(self, content: "ExtractedContent", **kwargs: Any) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        frontmatter = self._format_frontmatter({
            "created": now,
            "modified": now,
            "tags": self._build_tags(content),
            "source-type": "collected",
            "source": "zhihu",
            "url": content.url,
            "author": content.author,
            "publish_date": content.publish_date,
            "status": "collected",
        })
        
        lines = [
            frontmatter,
            "",
            f"# {content.title}",
            "",
            f"> **作者**: [{content.author}](https://www.zhihu.com/people/{content.author})",
        ]
        
        if content.publish_date:
            lines.append(f"> **发布时间**: {content.publish_date}")
        
        lines.append("")
        
        if content.summary:
            lines.extend(["## 摘要", "", content.summary, ""])
        
        lines.extend(["## 正文", "", content.content, ""])
        
        lines.extend([
            "## 来源",
            "",
            f"- **原文**: [{content.title}]({content.url})",
            f"- **作者**: {content.author}",
            "",
            "---",
            "",
        ])
        
        return "\n".join(lines)
    
    def _build_tags(self, content: "ExtractedContent") -> list[str]:
        tags = ["collected", "zhihu"]
        if content.topic:
            tags.append(content.topic)
        tags.extend(content.tags)
        return list(set(tags))


class ArticleTemplate(BaseTemplate):
    """通用文章模板."""
    
    name = "articles"
    
    def render(self, content: "ExtractedContent", **kwargs: Any) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        frontmatter = self._format_frontmatter({
            "created": now,
            "modified": now,
            "tags": self._build_tags(content),
            "source-type": "collected",
            "source": content.site_type or "web",
            "url": content.url,
            "author": content.author,
            "site": content.site_name,
            "publish_date": content.publish_date,
            "status": "collected",
        })
        
        lines = [
            frontmatter,
            "",
            f"# {content.title}",
            "",
        ]
        
        # 元信息
        meta_lines = []
        if content.author:
            meta_lines.append(f"**作者**: {content.author}")
        if content.site_name:
            meta_lines.append(f"**来源**: {content.site_name}")
        if content.publish_date:
            meta_lines.append(f"**发布时间**: {content.publish_date}")
        if content.word_count:
            meta_lines.append(f"**字数**: {content.word_count}")
        
        if meta_lines:
            lines.append("> " + " | ".join(meta_lines))
            lines.append("")
        
        if content.summary:
            lines.extend(["## 摘要", "", content.summary, ""])
        
        lines.extend(["## 正文", "", content.content, ""])
        
        lines.extend([
            "## 来源",
            "",
            f"- **原文**: [{content.title}]({content.url})",
        ])
        if content.author:
            lines.append(f"- **作者**: {content.author}")
        
        lines.extend(["", "---", ""])
        
        return "\n".join(lines)
    
    def _build_tags(self, content: "ExtractedContent") -> list[str]:
        tags = ["collected"]
        if content.site_type:
            tags.append(content.site_type)
        if content.topic:
            tags.append(content.topic)
        tags.extend(content.tags)
        return list(set(tags))


class TemplateRegistry:
    """模板注册表."""
    
    _templates: dict[str, type[BaseTemplate]] = {
        "wechat": WechatTemplate,
        "zhihu": ZhihuTemplate,
        "articles": ArticleTemplate,
        "web": ArticleTemplate,
    }
    
    @classmethod
    def get(cls, site_type: str) -> BaseTemplate:
        """获取对应类型的模板实例."""
        template_class = cls._templates.get(site_type, ArticleTemplate)
        return template_class()
    
    @classmethod
    def register(cls, site_type: str, template_class: type[BaseTemplate]) -> None:
        """注册新模板."""
        cls._templates[site_type] = template_class
    
    @classmethod
    def list_templates(cls) -> list[str]:
        """列出所有可用模板."""
        return list(cls._templates.keys())
