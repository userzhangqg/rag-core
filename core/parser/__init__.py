#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文档解析器模块

该模块提供了统一的文档解析接口，支持多种文档格式的解析。
使用工厂模式和策略模式实现高度可扩展的架构。

支持的文档格式：
- PDF (.pdf)
- Markdown (.md, .markdown)
- DOCX (.docx, .doc)
- Excel (.xlsx, .xls)
- PowerPoint (.pptx, .ppt)
- HTML (.html, .htm)
- 文本文件 (.txt, .text)

使用示例：
    from core.parser.factory import ParserFactory
    
    # 根据文件类型自动选择解析器
    parser = ParserFactory.auto_detect_parser("document.pdf")
    documents = parser.parse("document.pdf")
    
    # 指定解析器类型
    parser = ParserFactory.create_parser("pdf", parser_type="fast")
    documents = parser.parse("document.pdf")
"""

from .base import BaseParser
from .factory import ParserFactory

# 导出基础解析器
from .pdf_simple_parser import PdfSimpleParser
from .pdf_mineru_parser import MineruVLMParser, MineruPipelineParser
from .markdown_parser import MarkdownParser

# 导出扩展解析器（可能未完全实现）
try:
    from .docx_parser import DocxParser
except ImportError:
    DocxParser = None

try:
    from .excel_parser import ExcelParser
except ImportError:
    ExcelParser = None

try:
    from .powerpoint_parser import PowerPointParser
except ImportError:
    PowerPointParser = None

try:
    from .html_parser import HtmlParser
except ImportError:
    HtmlParser = None

try:
    from .text_parser import TextParser
except ImportError:
    TextParser = None

__all__ = [
    "BaseParser",
    "ParserFactory",
    "PdfSimpleParser",
    "MineruVLMParser",
    "MineruPipelineParser",
    "MarkdownParser",
    "DocxParser",
    "ExcelParser",
    "PowerPointParser",
    "HtmlParser",
    "TextParser"
]