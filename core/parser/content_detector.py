#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
内容类型检测器
用于智能检测文本内容的类型，自动选择合适的解析器
"""

import re
from typing import Dict, Optional


class ContentDetector:
    """
    智能内容类型检测器
    根据内容特征自动识别文本类型
    """
    
    # Markdown特征正则表达式
    MARKDOWN_PATTERNS = {
        'headers': re.compile(r'^#{1,6}\s+.*$', re.MULTILINE),
        'code_blocks': re.compile(r'```.*?```', re.DOTALL),
        'inline_code': re.compile(r'`[^`]+`'),
        'bold': re.compile(r'\*\*[^*]+\*\*|__[^_]+__'),
        'italic': re.compile(r'\*[^*]+\*|_[^_]+_'),
        'links': re.compile(r'\[([^\]]+)\]\([^)]+\)'),
        'images': re.compile(r'!\[([^\]]*)\]\([^)]+\)'),
        'lists': re.compile(r'^(\s*[-*+]\s+|\s*\d+\.\s+)', re.MULTILINE),
        'tables': re.compile(r'\|.*\|.*\|', re.MULTILINE),
        'horizontal_rules': re.compile(r'^\s*[-*_]{3,}\s*$', re.MULTILINE)
    }
    
    # HTML特征正则表达式
    HTML_PATTERNS = {
        'tags': re.compile(r'<[^>]+>'),
        'doctype': re.compile(r'<!DOCTYPE[^>]*>', re.IGNORECASE),
        'html_entities': re.compile(r'&[a-zA-Z0-9#]+;'),
        'comments': re.compile(r'<!--.*?-->', re.DOTALL),
        'basic_structure': re.compile(r'<(html|head|body|div|p|br|h[1-6]|ul|ol|li|a|img)[^>]*>', re.IGNORECASE)
    }
    
    @classmethod
    def detect_content_type(cls, content: str) -> Dict[str, float]:
        """
        检测内容类型并返回置信度分数
        
        Args:
            content: 待检测的文本内容
            
        Returns:
            Dict[str, float]: 各类型置信度分数
        """
        if not content:
            return {'text': 1.0, 'markdown': 0.0, 'html': 0.0}
        
        content = content.strip()
        
        # 计算各类型特征匹配度
        markdown_score = cls._calculate_markdown_score(content)
        html_score = cls._calculate_html_score(content)
        
        # 如果都不是很高，默认为文本
        if markdown_score < 0.1 and html_score < 0.1:
            return {'text': 1.0, 'markdown': 0.0, 'html': 0.0}
        
        # 归一化分数
        total = markdown_score + html_score
        if total == 0:
            return {'text': 1.0, 'markdown': 0.0, 'html': 0.0}
        
        return {
            'text': max(0.0, 1.0 - markdown_score - html_score),
            'markdown': markdown_score / total if total > 0 else 0.0,
            'html': html_score / total if total > 0 else 0.0
        }
    
    @classmethod
    def _calculate_markdown_score(cls, content: str) -> float:
        """计算Markdown特征匹配分数"""
        total_patterns = len(cls.MARKDOWN_PATTERNS)
        matched_patterns = 0
        
        for pattern_name, pattern in cls.MARKDOWN_PATTERNS.items():
            if pattern.search(content):
                matched_patterns += 1
        
        # 权重调整：标题和列表更重要
        score = matched_patterns / total_patterns
        
        # 如果有标题，直接给高分
        if cls.MARKDOWN_PATTERNS['headers'].search(content):
            score = max(score, 0.8)
        
        # 如果有代码块，也给高分
        if cls.MARKDOWN_PATTERNS['code_blocks'].search(content):
            score = max(score, 0.7)
        
        return min(1.0, score)
    
    @classmethod
    def _calculate_html_score(cls, content: str) -> float:
        """计算HTML特征匹配分数"""
        total_patterns = len(cls.HTML_PATTERNS)
        matched_patterns = 0
        
        for pattern_name, pattern in cls.HTML_PATTERNS.items():
            if pattern.search(content):
                matched_patterns += 1
        
        # 权重调整：基本结构和doctype更重要
        if cls.HTML_PATTERNS['basic_structure'].search(content):
            matched_patterns += 3  # HTML标签是强特征
        
        if cls.HTML_PATTERNS['doctype'].search(content):
            matched_patterns += 2  # DOCTYPE是强特征
        
        return min(1.0, matched_patterns / (total_patterns + 3))
    
    @classmethod
    def select_parser_type(cls, content: str, threshold: float = 0.1) -> str:
        """
        根据内容选择最佳解析器类型
        
        Args:
            content: 待检测的文本内容
            threshold: 置信度阈值
            
        Returns:
            str: 推荐的解析器类型 ('text', 'markdown', 'html')
        """
        # 优先检查是否有HTML标签
        if cls.HTML_PATTERNS['tags'].search(content):
            # 检查是否是完整的HTML结构
            if cls.HTML_PATTERNS['basic_structure'].search(content) or cls.HTML_PATTERNS['doctype'].search(content):
                return 'html'
        
        # 检查Markdown特征
        if cls.MARKDOWN_PATTERNS['headers'].search(content):
            return 'markdown'
        
        # 检查是否有其他Markdown特征
        markdown_features = [
            cls.MARKDOWN_PATTERNS['code_blocks'],
            cls.MARKDOWN_PATTERNS['lists'],
            cls.MARKDOWN_PATTERNS['links'],
            cls.MARKDOWN_PATTERNS['tables']
        ]
        
        for pattern in markdown_features:
            if pattern.search(content):
                return 'markdown'
        
        # 默认返回text
        return 'text'
    
    @classmethod
    def is_likely_markdown(cls, content: str, threshold: float = 0.3) -> bool:
        """判断内容是否可能是Markdown"""
        scores = cls.detect_content_type(content)
        return scores['markdown'] >= threshold
    
    @classmethod
    def is_likely_html(cls, content: str, threshold: float = 0.3) -> bool:
        """判断内容是否可能是HTML"""
        scores = cls.detect_content_type(content)
        return scores['html'] >= threshold