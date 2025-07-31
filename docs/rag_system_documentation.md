# RAG知识库系统文档

## 系统概述

RAG知识库系统是一个基于检索增强生成（Retrieval-Augmented Generation）技术的文档处理和信息检索系统。该系统支持多种文档格式的解析、智能分块、向量存储和语义检索功能。

### 核心功能

1. **文档解析**：支持Markdown、PDF等多种格式文档的解析
2. **智能分块**：基于语义的文本分块，保持内容完整性
3. **章节解析**：按标题层级解析文档结构
4. **元数据管理**：为每个文本块添加丰富的元数据信息
5. **表格提取**：从文档中提取表格内容
6. **RAG流程**：完整的检索增强生成处理流程

### 技术架构

系统采用模块化设计，主要包括以下组件：

- **Parser（解析器）**：负责文档解析和内容提取
- **Chunking（分块器）**：将文档内容分割成适当大小的文本块
- **Pipeline（流程）**：协调整个RAG处理流程
- **Retrieval（检索器）**：实现向量检索和混合检索
- **Reranker（重排序器）**：对检索结果进行重排序优化
- **LLM（大语言模型）**：生成式问答和内容处理
- **Vector（向量存储）**：向量数据库存储和管理

## 核心模块详解

### 1. Markdown解析器

Markdown解析器（`MarkdownParser`）是系统的核心组件之一，支持多种解析模式：

#### 基本解析

基本解析将文档按元素分割成多个文档对象：

```python
from core.parser.markdown_parser import MarkdownParser

parser = MarkdownParser()
documents = parser.parse("document.md", source_type="file")
```

#### 章节解析

章节解析按标题层级将文档组织成结构化的章节：

```python
sections = parser.parse_with_sections("document.md", source_type="file")
```

章节解析的特点：
- 按标题层级组织内容
- 保留章节元数据（标题、层级、行号等）
- 支持嵌套标题结构
- 处理无标题内容

#### 表格提取

从文档中提取表格内容：

```python
text_without_tables, tables = parser.extract_tables(content)
```

### 2. 文本分块器

文本分块器（`RecursiveCharTextChunk`）基于LangChain的递归字符分割器实现：

```python
from core.chunking.recursive_char_text_chunk import RecursiveCharTextChunk

chunker = RecursiveCharTextChunk(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)
chunks = chunker.get_chunks(paragraphs)
```

### 3. RAG流程管道

RAG流程管道（`RAGPipeline`）协调整个文档处理流程：

#### 基本使用

```python
from core.pipeline.rag_pipeline import RAGPipeline, RAGConfig

# 使用默认配置
pipeline = RAGPipeline()

# 处理文件
chunks = pipeline.process_file("document.md")

# 处理文本内容
chunks = pipeline.process_content(content, source_name="custom_content")
```

#### 配置选项

```python
config = RAGConfig(
    chunk_size=800,
    chunk_overlap=150,
    parse_by_chapter=True,  # 启用章节解析
    remove_hyperlinks=True, # 移除超链接
    remove_images=True      # 移除图片
)
pipeline = RAGPipeline(config)
```

#### 批量处理

```python
# 处理整个目录
results = pipeline.process_directory("/path/to/documents")
```

## 使用示例

### 示例1：基本文档处理

```python
import tempfile
import os
from core.pipeline.rag_pipeline import RAGPipeline

# 创建示例文档
content = """
# 机器学习基础

## 什么是机器学习

机器学习是人工智能的一个分支...
"""

# 处理内容
pipeline = RAGPipeline()
chunks = pipeline.process_content(content, source_name="ml_basics")

print(f"生成了 {len(chunks)} 个文本分块")
for i, chunk in enumerate(chunks[:3]):
    print(f"分块 {i+1}: {len(chunk['text'])} 字符")
```

### 示例2：章节解析对比

```python
from core.parser.markdown_parser import MarkdownParser
from core.pipeline.rag_pipeline import RAGPipeline, RAGConfig

# 创建复杂文档
content = """
# 深度学习

## 神经网络基础

### 感知机
感知机是最简单的神经网络单元。

## 卷积神经网络
CNN在图像处理中表现出色。
"""

parser = MarkdownParser()

# 传统解析
traditional_docs = parser.parse(content, source_type="content")
print(f"传统解析: {len(traditional_docs)} 个文档")

# 章节解析
section_docs = parser.parse_with_sections(content, source_type="content")
print(f"章节解析: {len(section_docs)} 个章节")

# RAG Pipeline对比
config_traditional = RAGConfig(parse_by_chapter=False)
pipeline_traditional = RAGPipeline(config_traditional)
chunks_traditional = pipeline_traditional.process_content(content)

config_chapter = RAGConfig(parse_by_chapter=True)
pipeline_chapter = RAGPipeline(config_chapter)
chunks_chapter = pipeline_chapter.process_content(content)

print(f"传统方式: {len(chunks_traditional)} 个分块")
print(f"章节方式: {len(chunks_chapter)} 个分块")
```

## 部署和运行

### 环境要求

- Python 3.11+
- 依赖包：详见 `requirements.txt`

### 安装步骤

1. 克隆项目代码
2. 安装依赖：`pip install -r requirements.txt`
3. 下载NLTK数据：`python download_nltk_data.py`

### 运行示例

```bash
# 运行章节解析演示
python examples/section_parsing_demo.py

# 运行基本使用示例
python examples/example_usage.py
```

## 开发计划

系统按以下阶段进行开发：

1. **需求分析和设计阶段**（第1-2周）
2. **核心功能开发阶段**（第3-6周）
3. **高级功能开发阶段**（第7-9周）
4. **集成测试阶段**（第10-11周）
5. **性能优化阶段**（第12周）
6. **部署和文档阶段**（第13周）

## API参考

### MarkdownParser

#### `parse(source, source_type="file")`

基本文档解析方法。

参数：
- `source`: 文件路径、内容字符串或字节流
- `source_type`: "file"、"content" 或 "bytes"

返回：
- `List[Document]`: 文档对象列表

#### `parse_with_sections(source, source_type="file")`

按章节解析文档。

参数：
- `source`: 文件路径、内容字符串或字节流
- `source_type`: "file"、"content" 或 "bytes"

返回：
- `List[Document]`: 按章节组织的文档对象列表

#### `extract_tables(content)`

提取文档中的表格。

参数：
- `content`: 文档内容字符串

返回：
- `tuple[str, List[str]]`: 去除表格后的内容和表格列表

### RAGPipeline

#### `process_file(file_path, custom_metadata=None)`

处理单个文件。

参数：
- `file_path`: 文件路径
- `custom_metadata`: 自定义元数据

返回：
- `List[Dict]`: 分块列表，每个包含text和metadata

#### `process_content(content, source_name="content", custom_metadata=None)`

处理文本内容。

参数：
- `content`: 文本内容
- `source_name`: 来源名称
- `custom_metadata`: 自定义元数据

返回：
- `List[Dict]`: 分块列表，每个包含text和metadata

#### `process_directory(directory, file_pattern="*.md", recursive=True, custom_metadata=None)`

批量处理目录。

参数：
- `directory`: 目录路径
- `file_pattern`: 文件匹配模式
- `recursive`: 是否递归子目录
- `custom_metadata`: 自定义元数据

返回：
- `Dict[str, List[Dict]]`: 文件路径到分块列表的映射