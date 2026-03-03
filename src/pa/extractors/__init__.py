"""内容提取器模块.

提供智能网页内容提取、元数据解析和图片本地化功能。
"""

from pa.extractors.models import ExtractedContent, ExtractedImage
from pa.extractors.base import BaseExtractor
from pa.extractors.web import WebExtractor
from pa.extractors.image_handler import ImageHandler

__all__ = [
    "ExtractedContent",
    "ExtractedImage",
    "BaseExtractor",
    "WebExtractor",
    "ImageHandler",
]
