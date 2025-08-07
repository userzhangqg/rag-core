#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTML文档解析器
用于解析HTML网页和文档，支持智能提取文本内容
"""

import re
from typing import List, Union
from langchain_core.documents.base import Document
from core.parser.base import BaseParser


class HtmlParser(BaseParser):
    """
    HTML文档解析器
    用于解析HTML网页和文档，支持从HTML中提取纯文本内容
    """
    
    supported_extensions = [".html", ".htm"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger.info("Initialized HtmlParser")
    
    def parse(self, source: Union[str, bytes], source_type: str = "file") -> List[Document]:
        """
        解析HTML文档内容
        
        Args:
            source: 文件路径、文件内容或字节流
            source_type: "file" | "content" | "bytes"
            
        Returns:
            List[Document]: 解析后的文档列表
        """
        self.logger.debug(f"Starting HTML parsing with source_type: {source_type}")

        self.logger.debug(f"Parser Config: {self.config}")
        if self.config.get("parse_by_chapter", False):
            self.logger.debug("Parsing HTML with sections")
            return self.parse_with_sections(source, source_type)
        
        try:
            if source_type == "file":
                with open(source, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif source_type == "content":
                content = source
            elif source_type == "bytes":
                content = source.decode('utf-8')
            else:
                raise ValueError(f"Unsupported source_type: {source_type}")
            
            # 提取纯文本内容
            text_content = self._extract_text_from_html(content)
            
            # 创建文档对象
            documents = [Document(
                page_content=text_content,
                metadata={
                    "source": str(source),
                    "type": "html",
                    "parser": "HtmlParser",
                    "original_length": len(content),
                    "extracted_length": len(text_content)
                }
            )]
            
            self.logger.info(f"Successfully parsed HTML content, extracted {len(text_content)} characters")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error parsing HTML file: {e}")
            return []
    
    def parse_by_sections(self, source: Union[str, bytes], 
                         source_type: str = "file") -> List[Document]:
        """
        按章节/标签解析HTML文档
        
        Args:
            source: 文件路径、文件内容或字节流
            source_type: "file" | "content" | "bytes"
            
        Returns:
            List[Document]: 按章节组织的文档列表
        """
        self.logger.debug(f"Starting HTML section parsing with source_type: {source_type}")
        
        try:
            if source_type == "file":
                with open(source, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif source_type == "content":
                content = source
            elif source_type == "bytes":
                content = source.decode('utf-8')
            else:
                raise ValueError(f"Unsupported source_type: {source_type}")
            
            # 按HTML标签分段
            sections = self._extract_sections_from_html(content)
            
            documents = []
            for i, section in enumerate(sections):
                if section.strip():
                    documents.append(Document(
                        page_content=section.strip(),
                        metadata={
                            "source": str(source),
                            "type": "html",
                            "parser": "HtmlParser",
                            "section": f"section_{i+1}",
                            "section_index": i + 1
                        }
                    ))
            
            self.logger.info(f"Successfully parsed {len(documents)} HTML sections")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error parsing HTML sections: {e}")
            return []
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """
        从HTML内容中提取纯文本
        
        Args:
            html_content: HTML内容
            
        Returns:
            str: 提取的纯文本
        """
        try:
            # 移除script和style标签
            content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            
            # 移除注释
            content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
            
            # 替换HTML标签为空格
            content = re.sub(r'<[^>]+>', ' ', content)
            
            # 处理HTML实体
            content = self._decode_html_entities(content)
            
            # 清理多余的空白字符
            content = re.sub(r'\s+', ' ', content).strip()
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error extracting text from HTML: {e}")
            return html_content
    
    def _extract_sections_from_html(self, html_content: str) -> List[str]:
        """
        从HTML内容中提取各个章节
        
        Args:
            html_content: HTML内容
            
        Returns:
            List[str]: 章节内容列表
        """
        try:
            # 简单的按块级元素分段
            block_elements = [
                'div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'ul', 'ol', 'li', 'table', 'tr', 'td', 'section', 'article'
            ]
            
            # 创建匹配块级元素的表达式
            pattern = r'<(?:' + '|'.join(block_elements) + r')[^>]*>.*?</(?:' + '|'.join(block_elements) + r')>'
            
            # 提取块级元素内容
            sections = []
            matches = re.findall(pattern, html_content, flags=re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                text = self._extract_text_from_html(match)
                if text.strip() and len(text.strip()) > 10:  # 过滤短内容
                    sections.append(text.strip())
            
            # 如果没有找到块级元素，按段落处理
            if not sections:
                text = self._extract_text_from_html(html_content)
                paragraphs = text.split('\n\n')
                sections = [p.strip() for p in paragraphs if p.strip()]
            
            return sections
            
        except Exception as e:
            self.logger.error(f"Error extracting HTML sections: {e}")
            return [self._extract_text_from_html(html_content)]
    
    def _decode_html_entities(self, text: str) -> str:
        """
        解码HTML实体
        
        Args:
            text: 包含HTML实体的文本
            
        Returns:
            str: 解码后的文本
        """
        html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&apos;': "'",
            '&#39;': "'",
            '&nbsp;': ' ',
            '&#160;': ' ',
            '&copy;': '©',
            '&reg;': '®',
            '&trade;': '™',
        }
        
        for entity, replacement in html_entities.items():
            text = text.replace(entity, replacement)
        
        return text