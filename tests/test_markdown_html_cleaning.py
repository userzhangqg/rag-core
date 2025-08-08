#!/usr/bin/env python3
"""
测试Markdown解析器的HTML标签清理功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.parser.markdown_parser import MarkdownParser

def test_html_cleaning():
    """测试HTML标签清理功能"""
    
    # 创建支持HTML清理的解析器
    parser = MarkdownParser(clean_html=True)
    
    # 测试用例1: 包含各种HTML标签的内容
    test_content1 = """
# 测试文档

这是一个段落，包含<span style="color:red">红色文本</span>和<div>div块内容</div>。

## 图片测试

<img src="https://example.com/image.jpg" alt="测试图片" />

## 表格测试

<table border="1">
<tr><th>列1</th><th>列2</th></tr>
<tr><td>数据1</td><td>数据2</td></tr>
</table>

## 链接测试

<a href="https://example.com">链接文本</a>

<p>段落标签</p>
<strong>粗体文本</strong>
"""
    
    # 测试用例2: 纯文本内容
    test_content2 = """
# 纯文本文档

这是没有HTML标签的纯文本内容。
- 列表项1
- 列表项2

普通段落文本。
"""
    
    # 测试用例3: 只有图片和表格
    test_content3 = """
# 只有图片和表格

<img src="https://example.com/image1.jpg" alt="图片1" />
<img src="https://example.com/image2.jpg" alt="图片2" />

<table>
<tr><td>表格内容</td></tr>
</table>
"""
    
    print("=== 测试HTML标签清理功能 ===\n")
    
    # 测试解析
    for i, content in enumerate([test_content1, test_content2, test_content3], 1):
        print(f"--- 测试用例 {i} ---")
        print("原始内容<<<<<<<<<<<<<<<<<<<<<<:")
        print(content)
        print("\n清理后的内容>>>>>>>>>>>>>>>>>>>:")
        
        try:
            cleaned = parser._clean_html_tags(content, preserve_imgs=True, preserve_tables=True)
            print(cleaned)
            print("\n")
        except Exception as e:
            print(f"错误: {e}")
            print("\n")
    
    print("=== 测试解析为文档 ===\n")
    
    # 测试解析为文档
    try:
        documents = parser.parse(test_content1, source_type="content")
        print(f"成功解析为 {len(documents)} 个文档")
        
        for doc_idx, doc in enumerate(documents):
            print(f"\n文档 {doc_idx + 1}:")
            print(f"内容长度: {len(doc.page_content)} 字符")
            print(f"内容预览: {doc.page_content[:200]}...")
            
    except Exception as e:
        print(f"解析错误: {e}")

def test_without_cleaning():
    """测试禁用HTML清理的情况"""
    print("\n=== 测试禁用HTML清理 ===\n")
    
    parser = MarkdownParser(clean_html=False)
    
    test_content = """
# 测试文档

<div>这个div标签应该保留</div>
<img src="test.jpg" alt="图片" />
"""
    
    try:
        cleaned = parser._clean_html_tags(test_content)
        print("禁用清理时的内容:")
        print(cleaned)
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_html_cleaning()
    test_without_cleaning()