#!/usr/bin/env python3
"""
按章节解析 Markdown 的测试用例
"""

import unittest
import tempfile
import os

import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.parser.markdown_parser import MarkdownParser
from core.pipeline.rag_pipeline import RAGPipeline, RAGConfig

class TestSectionParser(unittest.TestCase):
    """测试按章节解析功能"""
    
    def setUp(self):
        """测试初始化"""
        self.parser = MarkdownParser()
        self.sample_content = """# 机器学习基础

## 引言
机器学习是人工智能的一个分支，专注于让计算机系统能够从数据中学习并改进性能，而无需进行显式编程。

### 历史背景
机器学习的发展可以追溯到20世纪50年代，经历了多个重要阶段。

## 主要算法类型

### 监督学习
监督学习使用标记数据来训练模型。

#### 线性回归
线性回归是最基础的监督学习算法之一。

#### 决策树
决策树通过一系列条件判断来进行分类或回归。

### 无监督学习
无监督学习处理未标记的数据。

## 总结
机器学习正在改变我们生活的方方面面。
"""
    
    def test_parse_by_sections_basic(self):
        """测试基本的章节解析"""
        sections = self.parser.parse_by_sections(self.sample_content)
        print(sections)
        
        # 验证解析出的章节数量
        self.assertEqual(len(sections), 9)
        
        # 验证章节标题和层级
        expected_titles = [
            ("机器学习基础", 1),
            ("引言", 2),
            ("历史背景", 3),
            ("主要算法类型", 2),
            ("监督学习", 3),
            ("线性回归", 4),
            ("决策树", 4),
            ("无监督学习", 3),
            ("总结", 2)
        ]
        
        for i, (expected_title, expected_level) in enumerate(expected_titles):
            self.assertEqual(sections[i].metadata['title'], expected_title)
            self.assertEqual(sections[i].metadata['level'], expected_level)
            self.assertEqual(sections[i].metadata['type'], 'section')
    
    def test_parse_by_sections_no_headers(self):
        """测试无标题内容的解析"""
        content = "这是一个没有标题的文档。\n\n这是第二段内容。"
        sections = self.parser.parse_by_sections(content)
        
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0].metadata['title'], 'Full Document')
        self.assertEqual(sections[0].metadata['level'], 0)
    
    def test_parse_by_sections_empty_content(self):
        """测试空内容解析"""
        sections = self.parser.parse_by_sections("")
        self.assertEqual(len(sections), 0)
    
    def test_parse_with_sections_file(self):
        """测试文件方式的章节解析"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(self.sample_content)
            temp_file = f.name
        
        try:
            sections = self.parser.parse_with_sections(temp_file, source_type="file")
            self.assertEqual(len(sections), 9)
            self.assertEqual(sections[0].metadata['title'], "机器学习基础")
        finally:
            os.unlink(temp_file)
    
    def test_parse_with_sections_content(self):
        """测试内容字符串方式的章节解析"""
        sections = self.parser.parse_with_sections(self.sample_content, source_type="content")
        self.assertEqual(len(sections), 9)
        self.assertEqual(sections[0].metadata['title'], "机器学习基础")
    
    def test_rag_pipeline_with_sections(self):
        """测试 RAGPipeline 的章节解析功能"""
        config = RAGConfig(parse_by_chapter=True).from_config_file()
        pipeline = RAGPipeline(config)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(self.sample_content)
            temp_file = f.name
        
        try:
            chunks = pipeline.process_file(temp_file)
            print(f"   生成了 {len(chunks)} 个分块")
            # 验证生成了分块
            self.assertGreater(len(chunks), 0)
            
            # 验证每个分块包含章节信息
            for chunk in chunks:
                print(chunk)
                self.assertIn('title', chunk.get('metadata', {}))
                self.assertIn('level', chunk.get('metadata', {}))
                
        finally:
            os.unlink(temp_file)
    
    def test_rag_pipeline_without_sections(self):
        """测试 RAGPipeline 的传统解析方式"""
        config = RAGConfig(parse_by_chapter=False).from_config_file()
        pipeline = RAGPipeline(config)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(self.sample_content)
            temp_file = f.name
        
        try:
            chunks = pipeline.process_file(temp_file)
            # 验证生成了分块
            self.assertGreater(len(chunks), 0)
            
            # 验证分块不包含章节信息（使用传统解析）
            # 注意：传统解析可能不包含 title 和 level 信息
            
        finally:
            os.unlink(temp_file)
    
    def test_section_content_preservation(self):
        """测试章节内容的完整性"""
        sections = self.parser.parse_by_sections(self.sample_content)
        
        # 验证第一个章节包含正确的内容
        intro_section = sections[1]  # "引言"章节
        self.assertIn("机器学习是人工智能的一个分支", intro_section.page_content)
        self.assertIn("无需进行显式编程", intro_section.page_content)
        
        # 验证历史背景章节
        history_section = sections[2]  # "历史背景"章节
        self.assertIn("可以追溯到20世纪50年代", history_section.page_content)
    
    def test_nested_headers(self):
        """测试嵌套标题的处理"""
        content = """# 主标题

## 二级标题1
内容1

### 三级标题1
内容2

### 三级标题2
内容3

## 二级标题2
内容4
"""
        
        sections = self.parser.parse_by_sections(content)
        print(sections)
        
        # 验证层级关系
        self.assertEqual(sections[0].metadata['level'], 1)  # 主标题
        self.assertEqual(sections[1].metadata['level'], 2)  # 二级标题1
        self.assertEqual(sections[2].metadata['level'], 3)  # 三级标题1
        self.assertEqual(sections[3].metadata['level'], 3)  # 三级标题2
        self.assertEqual(sections[4].metadata['level'], 2)  # 二级标题2

if __name__ == '__main__':
    unittest.main()