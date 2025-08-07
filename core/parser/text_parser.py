#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文本文档解析器
用于解析纯文本文件
"""

from typing import List, Union
from langchain_core.documents.base import Document
from core.parser.base import BaseParser


class TextParser(BaseParser):
    """
    纯文本文件解析器
    用于解析.txt等纯文本文件
    """
    
    supported_extensions = [".txt", ".text"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger.info("Initialized TextParser")
    
    def parse(self, source: Union[str, bytes], source_type: str = "file") -> List[Document]:
        """
        解析文本文件内容
        
        Args:
            source: 文件路径、文件内容或字节流
            source_type: "file" | "content" | "bytes"
            
        Returns:
            List[Document]: 解析后的文档列表
        """
        self.logger.debug(f"Starting text parsing with source_type: {source_type}")

        self.logger.debug(f"Parser Config: {self.config}")
        if self.config.get("parse_by_chapter", False):
            self.logger.debug("Parsing text with sections")
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
            
            # 创建文档对象
            documents = [Document(
                page_content=content,
                metadata={
                    "source": str(source),
                    "type": "text",
                    "parser": "TextParser"
                }
            )]
            
            return documents
            
        except Exception as e:
            self.logger.error(f"Error parsing text file: {e}")
            return []
    
    def parse_with_sections(self, source: Union[str, bytes], 
                           source_type: str = "file") -> List[Document]:
        """
        按段落解析文本文件
        
        Args:
            source: 文件路径、文件内容或字节流
            source_type: "file" | "content" | "bytes"
            
        Returns:
            List[Document]: 按段落组织的文档列表
        """
        documents = self.parse(source, source_type)
        
        # 简单的按空行分段
        if documents and documents[0].page_content:
            paragraphs = documents[0].page_content.strip().split('\n\n')
            
            documents = []
            for i, para in enumerate(paragraphs):
                if para.strip():
                    documents.append(Document(
                        page_content=para.strip(),
                        metadata={
                            "source": str(source),
                            "type": "text",
                            "parser": "TextParser",
                            "section": f"paragraph_{i+1}"
                        }
                    ))
        
        return documents