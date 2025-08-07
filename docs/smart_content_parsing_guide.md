# 智能内容解析功能使用指南

## 功能概述

智能内容解析功能可以根据文本内容的特征自动选择合适的解析器，支持以下三种解析器：

- **Markdown解析器**：当内容包含标题、代码块、列表等Markdown特征时自动选择
- **HTML解析器**：当内容包含HTML标签、DOCTYPE声明等HTML特征时自动选择  
- **文本解析器**：当内容为纯文本时使用

## 核心组件

### 1. ContentDetector（内容检测器）
- 文件路径：`core/parser/content_detector.py`
- 功能：基于正则表达式检测内容类型特征
- 支持的特征：
  - Markdown：标题、代码块、列表、链接、表格等
  - HTML：标签、DOCTYPE、HTML实体、注释等

### 2. ParserFactory（解析器工厂）
- 文件路径：`core/parser/factory.py`
- 功能：根据内容特征智能创建解析器实例
- 关键方法：
  - `create_smart_parser_for_content(content)`: 根据内容选择解析器
  - `select_parser_type(content)`: 返回推荐解析器类型

### 3. 预处理管道集成
- 文件路径：`core/pipeline/preprocessing_pipeline.py`
- 功能：在process_content方法中自动使用智能解析

## 使用方法

### 基本使用

```python
from core.parser.factory import ParserFactory

# 智能选择解析器
content = "# 标题\n这是Markdown内容"
parser = ParserFactory.create_smart_parser_for_content(content)
documents = parser.parse(content, source_type="content")
```

### 强制指定解析器

```python
# 强制使用特定解析器
parser = ParserFactory.create_smart_parser_for_content(
    content, parser_type="markdown"  # 可选：markdown/html/text
)
```

### 文件处理

```python
from core.pipeline.preprocessing_pipeline import DocumentProcessingPipeline

# 自动使用智能解析
pipeline = DocumentProcessingPipeline()
documents = pipeline.process_content("# 标题\n内容", "test.md")
```

## 支持的文件类型

| 扩展名 | 解析器类型 |
|--------|------------|
| .md, .markdown | Markdown解析器 |
| .html, .htm | HTML解析器 |
| .txt, .text | 文本解析器 |

## 测试验证

运行测试验证功能：
```bash
python -m pytest tests/test_smart_parsing.py -v
```

运行示例演示：
```bash
python examples/smart_content_parsing.py
```

## 技术特点

1. **智能识别**：基于内容特征而非仅文件扩展名
2. **高准确率**：使用多重特征匹配算法
3. **可扩展性**：易于添加新的内容类型检测
4. **向后兼容**：支持强制指定解析器类型
5. **性能优化**：轻量级正则表达式检测

## 集成说明

该功能已集成到RAG系统的核心流程中，无需额外配置即可使用。预处理管道会自动根据内容特征选择最合适的解析器，确保最佳的解析效果。