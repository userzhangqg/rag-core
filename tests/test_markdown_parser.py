#!/usr/bin/env python3

"""测试MarkdownParser的简单脚本"""

import os
import sys
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.parser.markdown_parser import MarkdownParser


def test_markdown_parser():
    # 创建测试用的markdown内容
    test_content = """
# 标题1

这是一个包含[链接](http://example.com)和![图片](image.jpg)的段落。

## 标题2

这是另一个段落，包含一些**粗体**和*斜体*文本。

### 表格示例

| 列1 | 列2 | 列3 |
|-----|-----|-----|
| A   | B   | C   |
| D   | E   | F   |

这是表格后的文本。
""".strip()

    # 创建临时测试文件
    test_file = "test.md"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_content)

    try:
        # 测试解析器
        parser = MarkdownParser(remove_hyperlinks=True, remove_images=True)
        
        # 测试从文件解析
        documents = parser.parse(test_file, source_type="file")
        print("从文件解析结果:")
        for i, doc in enumerate(documents):
            print(f"  Document {i+1}: {doc.page_content[:50]}...")
        
        # 测试从内容解析
        documents = parser.parse(test_content, source_type="content")
        print("\n从内容解析结果:")
        for i, doc in enumerate(documents):
            print(f"  Document {i+1}: {doc.page_content[:50]}...")
            
        # 测试表格提取
        text_without_tables, tables = parser.extract_tables(test_content)
        print("\n表格提取结果:")
        print(f"  提取到的表格数量: {len(tables)}")
        print(f"  原文中的表格标记: {text_without_tables.count('[TABLE]')}个")
        print(f"  原文中的表格内容: \n {tables}", end='\n\t')
        
    finally:
        # 清理临时文件
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    test_markdown_parser()