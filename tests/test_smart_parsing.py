#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能内容解析测试
测试智能解析器选择和内容类型检测功能
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.parser.factory import ParserFactory
from core.parser.content_detector import ContentDetector
from core.parser.text_parser import TextParser
from core.parser.html_parser import HtmlParser
from core.parser.markdown_parser import MarkdownParser


class TestSmartParsing(unittest.TestCase):
    """测试智能解析功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.markdown_content = """# 标题
## 子标题
- 列表项1
- 列表项2
```python
print("hello")
```"""
        
        self.html_content = """<!DOCTYPE html>
<html>
<head><title>测试</title></head>
<body>
    <h1>标题</h1>
    <p>段落内容</p>
</body>
</html>"""
        
        self.text_content = """这是一个纯文本内容。
没有任何特殊格式。
就是普通文字。"""
    
    def test_content_type_detection(self):
        """测试内容类型检测"""
        # 测试Markdown检测
        scores = ContentDetector.detect_content_type(self.markdown_content)
        self.assertGreater(scores['markdown'], 0.5)
        self.assertIsInstance(scores, dict)
        self.assertIn('markdown', scores)
        self.assertIn('html', scores)
        self.assertIn('text', scores)
    
    def test_parser_type_selection(self):
        """测试解析器类型选择"""
        # Markdown内容应选择markdown解析器
        parser_type = ContentDetector.select_parser_type(self.markdown_content)
        self.assertEqual(parser_type, 'markdown')
        
        # HTML内容应选择html解析器
        parser_type = ContentDetector.select_parser_type(self.html_content)
        self.assertEqual(parser_type, 'html')
        
        # 纯文本应选择text解析器
        parser_type = ContentDetector.select_parser_type(self.text_content)
        self.assertEqual(parser_type, 'text')
    
    def test_smart_parser_creation(self):
        """测试智能解析器创建"""
        # Markdown内容应创建MarkdownParser
        parser = ParserFactory.create_smart_parser_for_content(self.markdown_content)
        self.assertIsInstance(parser, MarkdownParser)
        
        # HTML内容应创建HtmlParser
        parser = ParserFactory.create_smart_parser_for_content(self.html_content)
        self.assertIsInstance(parser, HtmlParser)
        
        # 纯文本应创建TextParser
        parser = ParserFactory.create_smart_parser_for_content(self.text_content)
        self.assertIsInstance(parser, TextParser)
    
    def test_parser_type_override(self):
        """测试解析器类型强制指定"""
        # 即使内容是Markdown，也可以强制使用text解析器
        parser = ParserFactory.create_smart_parser_for_content(
            self.markdown_content, parser_type="text"
        )
        self.assertIsInstance(parser, TextParser)
    
    def test_content_parsing(self):
        """测试内容解析"""
        # 测试Markdown解析
        parser = ParserFactory.create_smart_parser_for_content(self.markdown_content)
        documents = parser.parse(self.markdown_content, source_type="content")
        self.assertGreater(len(documents), 0)
        # 检查是否成功解析，不依赖特定的元数据格式
        self.assertIsInstance(documents, list)
        self.assertTrue(all(hasattr(doc, 'page_content') for doc in documents))
        
        # 测试HTML解析
        parser = ParserFactory.create_smart_parser_for_content(self.html_content)
        documents = parser.parse(self.html_content, source_type="content")
        self.assertGreater(len(documents), 0)
        self.assertIsInstance(documents, list)
        self.assertTrue(all(hasattr(doc, 'page_content') for doc in documents))
        
        # 测试文本解析
        parser = ParserFactory.create_smart_parser_for_content(self.text_content)
        documents = parser.parse(self.text_content, source_type="content")
        self.assertGreater(len(documents), 0)
        self.assertIsInstance(documents, list)
        self.assertTrue(all(hasattr(doc, 'page_content') for doc in documents))
    
    def test_edge_cases(self):
        """测试边界情况"""
        # 空内容
        empty_content = ""
        parser_type = ContentDetector.select_parser_type(empty_content)
        self.assertEqual(parser_type, 'text')
        
        # 非常短的内容
        short_content = "a"
        parser_type = ContentDetector.select_parser_type(short_content)
        self.assertEqual(parser_type, 'text')
        
        # 混合内容（同时有HTML和Markdown特征）
        mixed_content = """# Markdown标题
<div>HTML内容</div>
- Markdown列表"""
        parser_type = ContentDetector.select_parser_type(mixed_content)
        # 应该选择置信度最高的类型
        self.assertIn(parser_type, ['markdown', 'html', 'text'])
    
    def test_factory_registration(self):
        """测试工厂注册"""
        # 检查支持的扩展名
        extensions = ParserFactory.get_supported_extensions()
        expected_extensions = ['.txt', '.text', '.html', '.htm', '.md', '.markdown']
        
        for ext in expected_extensions:
            self.assertIn(ext.lower(), [e.lower() for e in extensions])


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)