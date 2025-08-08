#!/usr/bin/env python3
"""
Markdown HTML标签清理功能演示

这个示例展示了如何使用MarkdownParser的HTML清理功能，
该功能使用BeautifulSoup来清理HTML标签，仅保留图片和表格。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.parser.markdown_parser import MarkdownParser

def demo_html_cleaning():
    """HTML标签清理功能演示"""
    
    print("=== Markdown HTML标签清理功能演示 ===\n")
    
    # 示例内容：包含各种HTML标签
    sample_content = """
# 技术文档示例

## 简介
这是一个包含HTML标签的<span style="color: blue;">Markdown</span>文档。

## 图片示例
以下是一个图片：
<img src="https://via.placeholder.com/150" alt="示例图片" width="150" height="150" />

## 表格示例
<table style="border: 1px solid black;">
    <thead>
        <tr>
            <th>功能</th>
            <th>状态</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>HTML清理</td>
            <td>已启用</td>
        </tr>
        <tr>
            <td>图片保留</td>
            <td>已启用</td>
        </tr>
    </tbody>
</table>

## 其他HTML元素
<div class="warning">
    <p><strong>警告：</strong>这个div和段落标签将被清理。</p>
</div>

<ul>
    <li>列表项1</li>
    <li>列表项2</li>
</ul>

<a href="https://example.com">这个链接也将被清理</a>
"""
    
    # 演示1：启用HTML清理
    print("--- 演示1：启用HTML清理 ---")
    parser_with_cleaning = MarkdownParser(clean_html=True)
    
    print("原始内容：")
    print(sample_content)
    print("\n" + "="*50 + "\n")
    
    try:
        documents = parser_with_cleaning.parse(sample_content, source_type="content")
        
        print("解析结果（启用HTML清理）：")
        for i, doc in enumerate(documents):
            print(f"\n文档 {i+1}:")
            print(f"内容：{doc.page_content}")
            print(f"元数据：{doc.metadata}")
            
    except Exception as e:
        print(f"解析错误：{e}")
    
    print("\n" + "="*70 + "\n")
    
    # 演示2：禁用HTML清理
    print("--- 演示2：禁用HTML清理 ---")
    parser_without_cleaning = MarkdownParser(clean_html=False)
    
    try:
        documents = parser_without_cleaning.parse(sample_content, source_type="content")
        
        print("解析结果（禁用HTML清理）：")
        for i, doc in enumerate(documents):
            print(f"\n文档 {i+1}:")
            print(f"内容：{doc.page_content[:300]}...")  # 只显示前300字符
            print(f"内容长度：{len(doc.page_content)} 字符")
            
    except Exception as e:
        print(f"解析错误：{e}")

def demo_config_usage():
    """演示如何通过配置使用HTML清理功能"""
    
    print("\n=== 配置使用演示 ===\n")
    
    # 从配置创建解析器
    config = {
        "clean_html": True,
        "remove_hyperlinks": False,
        "remove_images": False
    }
    
    parser = MarkdownParser(**config)
    
    content_with_html = """
# 配置测试

<div>这个div标签将被清理</div>
<img src="config_test.jpg" alt="配置测试图片" />
"""
    
    try:
        documents = parser.parse(content_with_html, source_type="content")
        print("使用配置创建的解析器结果：")
        for doc in documents:
            print(f"内容：{doc.page_content}")
            
    except Exception as e:
        print(f"错误：{e}")

def demo_section_cleaning():
    """演示章节解析时的HTML清理"""
    
    print("\n=== 章节解析HTML清理演示 ===\n")
    
    content_with_sections = """
# 主标题

<div>介绍内容</div>

## 第一节
<p>第一节的内容</p>
<img src="section1.jpg" alt="第一节图片" />

### 子节1.1
<span>子节内容</span>

## 第二节
<table><tr><td>第二节表格</td></tr></table>
"""
    
    parser = MarkdownParser(clean_html=True)
    
    try:
        # 使用章节解析
        documents = parser.parse_with_sections(content_with_sections, source_type="content")
        
        print("章节解析结果：")
        for i, doc in enumerate(documents):
            print(f"\n章节 {i+1}:")
            print(f"标题：{doc.metadata.get('title', '无标题')}")
            print(f"内容：{doc.page_content}")
            
    except Exception as e:
        print(f"章节解析错误：{e}")

if __name__ == "__main__":
    demo_html_cleaning()
    demo_config_usage()
    demo_section_cleaning()