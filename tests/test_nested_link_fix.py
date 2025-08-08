#!/usr/bin/env python3

"""测试修复后的嵌套链接处理"""

import os
import sys
import re
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.parser.markdown_parser import MarkdownParser


def test_nested_link_fix():
    """测试嵌套链接的正确处理"""
    
    # 创建测试内容
    test_content = """
# 测试嵌套链接

这是一个嵌套链接：[![Deploy on Sealos](https://sealos.io/Deploy-on-Sealos.svg)](https://template.sealos.io/deploy?templateName=refly)

这是一个普通链接：[普通链接](http://example.com)

这是一个普通图片：![普通图片](image.jpg)

这是另一个嵌套链接：[![图片](image2.jpg)](http://example2.com)
""".strip()

    # 测试只移除超链接的情况
    parser = MarkdownParser(remove_hyperlinks=True, remove_images=False)
    documents = parser.parse(test_content, source_type="content")
    
    print("=== 只移除超链接的测试结果 ===")
    for i, doc in enumerate(documents):
        print(f"Document {i+1}: {repr(doc.page_content)}")
        
    # 验证嵌套链接的处理结果
    expected_results = [
        "![Deploy on Sealos](https://sealos.io/Deploy-on-Sealos.svg)",  # 应该保留内层图片
        "普通链接",  # 应该移除普通链接，保留文字
        "![普通图片](image.jpg)",  # 应该保留普通图片
        "![图片](image2.jpg)"  # 应该保留内层图片
    ]
    
    # 检查所有文档内容
    all_content = " ".join([doc.page_content for doc in documents])
    
    print("\n=== 验证结果 ===")
    for expected in expected_results:
        if expected in all_content:
            print(f"✓ 找到预期内容: {expected}")
        else:
            print(f"✗ 未找到预期内容: {expected}")
            
    # 测试不应出现的内容
    should_not_appear = [
        "[![Deploy on Sealos](https://sealos.io/Deploy-on-Sealos.svg)](https://template.sealos.io/deploy?templateName=refly)",
        "[普通链接](http://example.com)",
        "[![图片](image2.jpg)](http://example2.com)"
    ]
    
    print("\n=== 检查不应出现的内容 ===")
    for not_expected in should_not_appear:
        if not_expected not in all_content:
            print(f"✓ 正确移除: {not_expected}")
        else:
            print(f"✗ 意外保留: {not_expected}")


def test_edge_cases():
    """测试边界情况"""
    
    # 测试复杂的嵌套情况
    edge_cases = [
        # 多层嵌套
        "[![图片](image.jpg)](link1) 和 [![图片2](image2.jpg)](link2)",
        # 链接中包含多个图片
        "[![图片1](img1.jpg) 文字 [![图片2](img2.jpg)](link2)",
        # 空链接
        "[![](image.jpg)](http://example.com)",
        # 复杂URL
        "[![测试](image.jpg)](https://example.com/path?param=value#anchor)"
    ]
    
    parser = MarkdownParser(remove_hyperlinks=True, remove_images=False)
    
    print("\n=== 边界情况测试 ===")
    for i, case in enumerate(edge_cases):
        print(f"\n边界情况 {i+1}: {case}")
        documents = parser.parse(case, source_type="content")
        for doc in documents:
            print(f"  结果: {repr(doc.page_content)}")


if __name__ == "__main__":
    test_nested_link_fix()
    test_edge_cases()