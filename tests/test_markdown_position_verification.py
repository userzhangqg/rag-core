#!/usr/bin/env python3
"""
详细验证HTML元素在原始位置保留的测试
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.parser.markdown_parser import MarkdownParser

def test_exact_position_preservation():
    """精确验证HTML元素在原始位置保留"""
    
    parser = MarkdownParser(clean_html=True)
    
    # 测试用例：精确的位置验证
    test_content = """# 测试标题

这是第一段文字，包含<span>span标签</span>内容。

<img src="image1.jpg" alt="第一张图片" />

<div class="container">
  <p>段落中的<img src="image2.jpg" alt="第二张图片" />嵌套图片</p>
  <table>
    <tr>
      <th>表头1</th>
      <th>表头2</th>
    </tr>
    <tr>
      <td>数据1</td>
      <td>数据2</td>
    </tr>
  </table>
</div>

<p>最后一个段落，包含<img src="image3.jpg" alt="第三张图片" />图片</p>

<table>
  <caption>表格标题</caption>
  <tr><td>简单表格</td></tr>
</table>

结束文字。"""
    
    print("=== 精确位置验证测试 ===")
    print("原始内容:")
    print(test_content)
    print("\n" + "="*60)
    
    try:
        cleaned = parser._clean_html_tags(test_content)
        print("清理后的内容:")
        print(cleaned)
        
        # 验证关键元素的位置
        print("\n" + "="*60)
        print("=== 位置验证结果 ===")
        
        # 检查图片标签
        img_tags = ['image1.jpg', 'image2.jpg', 'image3.jpg']
        for img in img_tags:
            if img in cleaned:
                print(f"✅ 图片 {img} 保留")
            else:
                print(f"❌ 图片 {img} 未找到")
        
        # 检查表格标签
        table_indicators = ['<table>', '<th>表头1</th>', '<td>数据1</td>']
        for indicator in table_indicators:
            if indicator in cleaned:
                print(f"✅ 表格元素 {indicator} 保留")
            else:
                print(f"❌ 表格元素 {indicator} 未找到")
        
        # 验证清理效果
        print("\n=== 清理效果验证 ===")
        unwanted_tags = ['<span>', '<div', '<p>', '<caption>']
        for tag in unwanted_tags:
            if tag not in cleaned:
                print(f"✅ {tag} 标签已被成功清理")
            else:
                print(f"❌ {tag} 标签仍存在")
        
        # 验证内容完整性
        preserved_texts = [
            "这是第一段文字",
            "段落中的嵌套图片",
            "最后一个段落",
            "结束文字"
        ]
        
        for text in preserved_texts:
            if text in cleaned:
                print(f"✅ 文本 '{text}' 保留")
            else:
                print(f"❌ 文本 '{text}' 丢失")
                
    except Exception as e:
        print(f"测试错误: {e}")

def test_markdown_format_preservation():
    """验证Markdown格式在清理过程中保留"""
    
    parser = MarkdownParser(clean_html=True)
    
    markdown_content = """# 主标题

## 子标题

这是**粗体文字**和*斜体文字*。

- 列表项1
- 列表项2

| 列1 | 列2 |
|-----|-----|
| 数据1 | 数据2 |

<img src="md_image.jpg" alt="Markdown图片" />

[链接文本](https://example.com)

> 引用块内容

```python
print("代码块")
```"""
    
    print("\n=== Markdown格式验证测试 ===")
    print("原始Markdown:")
    print(markdown_content)
    print("\n" + "="*50)
    
    try:
        cleaned = parser._clean_html_tags(markdown_content)
        print("清理后的Markdown:")
        print(cleaned)
        
        # 验证Markdown格式
        print("\n=== Markdown格式验证 ===")
        markdown_elements = [
            ('# 主标题', '主标题'),
            ('**粗体文字**', '粗体'),
            ('*斜体文字*', '斜体'),
            ('| 列1 | 列2 |', '表格'),
            ('[链接文本](https://example.com)', '链接'),
            ('> 引用块', '引用'),
            ('```python', '代码块'),
            ('<img src="md_image.jpg"', '图片')
        ]
        
        for element, description in markdown_elements:
            if element in cleaned:
                print(f"✅ {description} 格式保留")
            else:
                print(f"❌ {description} 格式丢失")
                
    except Exception as e:
        print(f"Markdown测试错误: {e}")

if __name__ == "__main__":
    test_exact_position_preservation()
    test_markdown_format_preservation()