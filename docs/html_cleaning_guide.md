# Markdown HTML标签清理功能指南

## 概述

MarkdownParser现在支持HTML标签清理功能，使用BeautifulSoup来解析和处理HTML内容，仅保留图片和表格元素，移除其他所有HTML标签。

## 功能特性

- **智能清理**: 使用BeautifulSoup解析HTML，确保准确识别和处理
- **保留关键元素**: 仅保留`<img>`图片和`<table>`表格及其子元素
- **可配置**: 可以通过参数控制是否启用清理功能
- **兼容性强**: 支持所有Markdown解析模式（普通解析和章节解析）

## 使用方法

### 基本使用

```python
from core.parser.markdown_parser import MarkdownParser

# 启用HTML清理（默认）
parser = MarkdownParser(clean_html=True)

# 禁用HTML清理
parser = MarkdownParser(clean_html=False)
```

### 配置参数

```python
config = {
    "clean_html": True,          # 启用HTML清理
    "remove_hyperlinks": False,  # 不移除超链接
    "remove_images": False       # 不移除图片
}

parser = MarkdownParser(**config)
```

### 示例代码

#### 示例1：基本HTML清理

```python
content = """
# 测试文档

<div>这个div标签将被清理</div>
<img src="image.jpg" alt="测试图片" />
<table><tr><td>表格内容</td></tr></table>
"""

parser = MarkdownParser(clean_html=True)
documents = parser.parse(content, source_type="content")
```

#### 示例2：章节解析时的HTML清理

```python
content = """
# 主标题

<div>介绍内容</div>

## 第一节
<p>第一节内容</p>
<img src="section1.jpg" />

## 第二节
<table><tr><td>表格数据</td></tr></table>
"""

parser = MarkdownParser(clean_html=True)
documents = parser.parse_with_sections(content, source_type="content")
```

## 清理规则

### 保留的元素

- `<img>`：图片元素及其所有属性
- `<table>`：表格元素及其所有子元素（`<tr>`, `<td>`, `<th>`, `<thead>`, `<tbody>`, `<tfoot>`等）

### 移除的元素

- 所有其他HTML标签（`<div>`, `<span>`, `<p>`, `<a>`, `<strong>`, `<em>`等）
- 样式属性
- 脚本标签
- 样式标签

### 处理流程

1. 使用BeautifulSoup解析HTML内容
2. 提取并保存所有图片和表格元素
3. 获取纯文本内容
4. 将保留的HTML元素重新附加到文本末尾

## 错误处理

当BeautifulSoup不可用或解析出错时，系统会：

- 记录警告日志
- 返回原始内容（不执行清理）
- 确保不影响正常解析流程

## 依赖要求

- `beautifulsoup4>=4.12.0`: HTML解析库
- `lxml>=4.9.0`: BeautifulSoup的lxml解析器

## 测试

运行测试验证功能：

```bash
# 运行HTML清理测试
python tests/test_markdown_html_cleaning.py

# 运行功能演示
python examples/markdown_html_cleaning_demo.py
```

## 注意事项

1. **性能考虑**: HTML清理会增加解析时间，对于大型文档可能影响性能
2. **格式保留**: 清理后的文本格式可能发生变化，建议测试验证
3. **图片和表格位置**: 保留的HTML元素会附加到文本末尾，可能改变原始布局
4. **配置优先**: 可以通过配置文件控制清理行为，避免硬编码

## 高级用法

### 自定义清理规则

如果需要自定义清理规则，可以继承MarkdownParser类并重写`_clean_html_tags`方法：

```python
from core.parser.markdown_parser import MarkdownParser

class CustomMarkdownParser(MarkdownParser):
    def _clean_html_tags(self, content: str) -> str:
        # 自定义清理逻辑
        # 返回清理后的内容
        pass
```

### 日志调试

启用调试日志查看详细的清理过程：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

parser = MarkdownParser(clean_html=True)
# 运行解析，查看详细日志
```