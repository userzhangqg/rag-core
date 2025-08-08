#!/usr/bin/env python3
"""
测试HTML元素在原始位置保留的功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.parser.markdown_parser import MarkdownParser

def test_html_position_preservation():
    """测试HTML元素是否在原始位置保留"""
    
    parser = MarkdownParser(clean_html=True)
    
    # 测试用例：HTML元素分布在不同位置
    test_content = """
# 标题

这是一个段落，包含<span>span标签</span>内容。

<img src="image1.jpg" alt="图片1" />

<div>这个div标签将被清理</div>

<table>
<tr><th>表头1</th><th>表头2</th></tr>
<tr><td>数据1</td><td>数据2</td></tr>
</table>

<p>另一个段落，包含<strong>粗体文本</strong>和<em>斜体文本</em>。</p>

<img src="image2.jpg" alt="图片2" />

<div>结束div</div>
"""
    
    print("=== 测试HTML元素位置保留 ===\n")
    print("原始内容:")
    print(test_content)
    print("\n" + "="*50 + "\n")
    
    try:
        cleaned = parser._clean_html_tags(test_content)
        print("清理后的内容:")
        print(cleaned)
        
        # 验证关键元素是否保留在正确位置
        lines = cleaned.split('\n')
        
        # 检查图片1是否在正确位置
        img1_line = None
        img2_line = None
        table_line = None
        
        for i, line in enumerate(lines):
            if '<img src="image1.jpg" alt="图片1"/>' in line:
                img1_line = i
            elif '<img src="image2.jpg" alt="图片2"/>' in line:
                img2_line = i
            elif '<table>' in line:
                table_line = i
        
        print(f"\n位置验证:")
        print(f"图片1位置: 第{img1_line + 1}行" if img1_line is not None else "图片1未找到")
        print(f"图片2位置: 第{img2_line + 1}行" if img2_line is not None else "图片2未找到")
        print(f"表格位置: 第{table_line + 1}行" if table_line is not None else "表格未找到")
        
        # 验证清理效果
        print(f"\n清理效果验证:")
        print(f"包含span标签: {'<span>' in cleaned}")
        print(f"包含div标签: {'<div>' in cleaned}")
        print(f"包含strong标签: {'<strong>' in cleaned}")
        print(f"包含em标签: {'<em>' in cleaned}")
        print(f"包含img标签: {'<img' in cleaned}")
        print(f"包含table标签: {'<table>' in cleaned}")
        
    except Exception as e:
        print(f"测试错误: {e}")

def test_mixed_content():
    """测试混合内容的位置保留"""
    
    parser = MarkdownParser(clean_html=True)
    
    # 测试嵌套内容
    nested_content = """
# 嵌套测试

<div>
  <p>段落中的<img src="nested.jpg" alt="嵌套图片" />图片</p>
  <table>
    <tr><td>嵌套表格</td></tr>
  </table>
</div>

<img src="standalone.jpg" alt="独立图片" />
"""
    
    print("\n=== 测试嵌套内容位置保留 ===\n")
    print("原始嵌套内容:")
    print(nested_content)
    print("\n" + "="*50 + "\n")
    
    try:
        cleaned = parser._clean_html_tags(nested_content)
        print("清理后的嵌套内容:")
        print(cleaned)
        
    except Exception as e:
        print(f"嵌套测试错误: {e}")

def test_markdown_with_html():
    """测试包含Markdown和HTML的混合内容"""
    
    parser = MarkdownParser(clean_html=True)
    
    markdown_content = """
# Markdown标题

这是**Markdown粗体**和*Markdown斜体*。

<img src="md_image.jpg" alt="Markdown图片" />

| 列1 | 列2 |
|-----|-----|
| 数据1 | 数据2 |

<div class="container">
  <span>HTML内容</span>
  <img src="html_image.jpg" alt="HTML图片" />
</div>

[链接文本](https://example.com)
"""
    
    print("\n=== 测试Markdown+HTML混合内容 ===\n")
    print("原始混合内容:")
    print(markdown_content)
    print("\n" + "="*50 + "\n")
    
    try:
        cleaned = parser._clean_html_tags(markdown_content)
        print("清理后的混合内容:")
        print(cleaned)
        
        # 验证Markdown格式是否保留
        print(f"\nMarkdown格式验证:")
        print(f"粗体格式保留: {'**Markdown粗体**' in cleaned}")
        print(f"斜体格式保留: {'*Markdown斜体*' in cleaned}")
        print(f"链接格式保留: {'[链接文本](https://example.com)' in cleaned}")
        
    except Exception as e:
        print(f"混合测试错误: {e}")

if __name__ == "__main__":
    test_html_position_preservation()
    test_mixed_content()
    test_markdown_with_html()