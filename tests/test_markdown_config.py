#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试MarkdownParser配置参数是否正确传递
"""

import unittest
from core.parser.markdown_parser import MarkdownParser
from core.parser.factory import ParserFactory


class TestMarkdownConfig(unittest.TestCase):
    
    def test_markdown_parser_config(self):
        """测试MarkdownParser配置参数"""
        # 测试默认参数
        parser = MarkdownParser()
        self.assertEqual(parser._markdown_clean_html, True)
        self.assertEqual(parser._markdown_preserve_html_imgs, False)
        self.assertEqual(parser._markdown_preserve_html_tables, True)
        
        # 测试自定义参数
        parser = MarkdownParser(markdown_clean_html=False, markdown_preserve_html_imgs=True, markdown_preserve_html_tables=False)
        self.assertEqual(parser._markdown_clean_html, False)
        self.assertEqual(parser._markdown_preserve_html_imgs, True)
        self.assertEqual(parser._markdown_preserve_html_tables, False)
    
    def test_parser_factory_config_passing(self):
        """测试ParserFactory是否正确传递配置参数"""
        # 初始化配置
        ParserFactory.initialize_config(
            markdown_clean_html=False,
            markdown_preserve_html_imgs=True,
            markdown_preserve_html_tables=False
        )
        
        # 创建MarkdownParser实例
        # parser = ParserFactory.create_parser("test.md", "default")
        parser = ParserFactory.auto_detect_parser("test.md")
        
        # 验证配置是否正确传递
        self.assertEqual(parser._markdown_clean_html, False)
        self.assertEqual(parser._markdown_preserve_html_imgs, True)
        self.assertEqual(parser._markdown_preserve_html_tables, False)


if __name__ == "__main__":
    unittest.main()