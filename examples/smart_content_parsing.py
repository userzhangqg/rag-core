#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能内容解析示例
展示如何使用基于内容特征的智能解析器选择功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.parser.factory import ParserFactory
from core.parser.content_detector import ContentDetector
from core.pipeline.preprocessing_pipeline import DocumentProcessingPipeline
from pathlib import Path


def demo_content_type_detection():
    """演示内容类型检测功能"""
    print("=== 内容类型检测演示 ===")
    
    # 测试不同类型的内容
    test_contents = [
        {
            "name": "Markdown内容",
            "content": """# 标题
这是一个Markdown文档

## 子标题
- 列表项1
- 列表项2

```python
print("Hello World")
```
"""
        },
        {
            "name": "HTML内容",
            "content": """<!DOCTYPE html>
<html>
<head>
    <title>示例页面</title>
</head>
<body>
    <h1>标题</h1>
    <p>这是一个段落</p>
    <ul>
        <li>列表项1</li>
        <li>列表项2</li>
    </ul>
</body>
</html>"""
        },
        {
            "name": "纯文本内容",
            "content": """这是一个纯文本内容。
没有任何特殊格式。
就是普通的文字内容。"""
        }
    ]
    
    for test in test_contents:
        print(f"\n--- {test['name']} ---")
        scores = ContentDetector.detect_content_type(test['content'])
        print(f"检测分数: {scores}")
        
        parser_type = ContentDetector.select_parser_type(test['content'])
        print(f"推荐解析器: {parser_type}")


def demo_smart_parser_selection():
    """演示智能解析器选择"""
    print("\n=== 智能解析器选择演示 ===")
    
    # 测试内容
    markdown_content = """# 项目介绍

## 功能特性
- 支持多种文档格式
- 智能内容识别
- 高性能处理

## 使用方法
```python
from core.parser.factory import ParserFactory
parser = ParserFactory.create_smart_parser_for_content(content)
```"""

    html_content = """<div>
    <h1>产品介绍</h1>
    <p>这是一个功能强大的产品，支持：</p>
    <ul>
        <li>多格式支持</li>
        <li>智能解析</li>
    </ul>
</div>"""

    text_content = """这是一个普通的文本内容，没有特殊的格式标记。
用于演示文本解析器的使用。"""

    contents = [
        ("Markdown", markdown_content),
        ("HTML", html_content),
        ("Text", text_content)
    ]
    
    for content_type, content in contents:
        print(f"\n--- {content_type}内容 ---")
        parser = ParserFactory.create_smart_parser_for_content(content)
        print(f"选择的解析器: {parser.__class__.__name__}")
        
        # 解析内容
        documents = parser.parse(content, source_type="content")
        print(f"解析结果: {len(documents)} 个文档")
        if documents:
            print(f"内容长度: {len(documents[0].page_content)} 字符")


def demo_pipeline_with_smart_parsing():
    """演示带智能解析的文档处理管道"""
    print("\n=== 文档处理管道演示 ===")
    
    # 创建处理管道
    pipeline = DocumentProcessingPipeline()
    
    # 测试不同格式的内容
    test_contents = [
        {
            "name": "markdown_example.md",
            "content": """# 技术文档

## 概述
这是一个技术文档的示例。

### 特性
- 支持Markdown格式
- 自动分块处理
- 智能内容识别

## 代码示例
```python
def hello_world():
    print("Hello, World!")
```"""
        },
        {
            "name": "html_example.html",
            "content": """<!DOCTYPE html>
<html>
<head><title>技术文档</title></head>
<body>
    <h1>技术文档</h1>
    <p>这是一个HTML格式的技术文档。</p>
    <h2>主要特性</h2>
    <ul>
        <li>HTML格式支持</li>
        <li>内容提取功能</li>
    </ul>
    <h2>使用说明</h2>
    <p>可以直接处理HTML内容并提取纯文本。</p>
</body>
</html>"""
        },
        {
            "name": "text_example.txt",
            "content": """这是一个纯文本格式的文档。

它包含了多个段落，用于演示文本处理功能。

第一段：介绍文档的基本信息。

第二段：说明文档的用途和处理方式。

第三段：总结文档的主要内容。"""
        }
    ]
    
    for test in test_contents:
        print(f"\n--- 处理 {test['name']} ---")
        
        # 使用管道处理内容
        chunks = pipeline.process_content(
            content=test['content'],
            source_name=test['name']
        )
        
        print(f"生成了 {len(chunks)} 个分块")
        
        # 显示前几个分块
        for i, chunk in enumerate(chunks[:3]):
            print(f"  分块 {i+1}: {len(chunk['text'])} 字符")
            if len(chunk['text']) > 50:
                print(f"    内容预览: {chunk['text'][:50]}...")
            else:
                print(f"    内容: {chunk['text']}")


def demo_file_processing():
    """演示文件处理"""
    print("\n=== 文件处理演示 ===")
    
    # 创建测试文件
    test_dir = Path("data/test_files")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建测试文件
    files = [
        ("sample.md", """# 测试文档
这是一个Markdown文件，用于测试智能解析功能。

## 功能列表
- 自动识别文件类型
- 智能选择解析器
- 高效处理内容"""),
        
        ("sample.txt", """这是一个纯文本文件。
用于测试文本解析器的功能。
包含多个段落和换行符。"""),
        
        ("sample.html", """<!DOCTYPE html>
<html>
<head><title>测试</title></head>
<body>
    <h1>测试文档</h1>
    <p>这是HTML格式的测试内容。</p>
</body>
</html>""")
    ]
    
    for filename, content in files:
        file_path = test_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # 处理文件
    pipeline = DocumentProcessingPipeline()
    
    for filename in ["sample.md", "sample.txt", "sample.html"]:
        file_path = test_dir / filename
        try:
            chunks = pipeline.process_file(str(file_path))
            print(f"{filename}: 生成了 {len(chunks)} 个分块")
        except Exception as e:
            print(f"{filename}: 处理失败 - {e}")


if __name__ == "__main__":
    try:
        demo_content_type_detection()
        demo_smart_parser_selection()
        demo_pipeline_with_smart_parsing()
        demo_file_processing()
        
        print("\n=== 演示完成 ===")
        print("智能内容解析功能已成功集成到系统中！")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()