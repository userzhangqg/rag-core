#!/usr/bin/env python3
"""
测试HTML元素位置保留功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.parser.markdown_parser import MarkdownParser

def test_html_position_preservation():
    """测试HTML元素位置保留"""
    parser = MarkdownParser(clean_html=True)
    
    # 测试用例1：简单图片
    content1 = '<p>这是一段文字 <img src="image1.jpg" alt="图片1" /> 继续文字</p>'
    result1 = parser._clean_html_tags(content1)
    print("测试1 - 简单图片:")
    print("原始:", content1)
    print("结果:", result1)
    print("图片是否保留:", '<img src="image1.jpg" alt="图片1" />' in result1)
    print()
    
    # 测试用例2：完整表格
    content2 = '''
    <div>
        <p>表格前的文字</p>
        <table>
            <thead>
                <tr><th>标题1</th><th>标题2</th></tr>
            </thead>
            <tbody>
                <tr><td>内容1</td><td>内容2</td></tr>
            </tbody>
        </table>
        <p>表格后的文字</p>
    </div>
    '''
    result2 = parser._clean_html_tags(content2)
    print("测试2 - 完整表格:")
    print("原始:", content2)
    print("结果:", result2)
    print("表格是否保留:", '<table>' in result2 and '</table>' in result2)
    print("tr标签是否保留:", '<tr>' in result2)
    print("td标签是否保留:", '<td>' in result2)
    print()
    
    # 测试用例3：混合内容
    content3 = '''
    <h1>标题</h1>
    <p>段落文字</p>
    <img src="image2.jpg" />
    <div>
        <table>
            <tr><td>嵌套表格</td></tr>
        </table>
    </div>
    <span>更多文字</span>
    '''
    result3 = parser._clean_html_tags(content3)
    print("测试3 - 混合内容:")
    print("原始:", content3)
    print("结果:", result3)
    print("图片是否保留:", 'image2.jpg' in result3)
    print("表格是否保留:", '<table>' in result3)
    print("div和span是否被移除:", '<div>' not in result3 and '<span>' not in result3)

if __name__ == "__main__":
    test_html_position_preservation()