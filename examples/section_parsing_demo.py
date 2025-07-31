#!/usr/bin/env python3
"""
按章节解析 Markdown 的综合演示

这个示例展示了如何使用新的按章节解析功能，
并与传统解析方式进行对比。
"""

import os
import sys
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.parser.markdown_parser import MarkdownParser
from core.pipeline.rag_pipeline import RAGPipeline, RAGConfig

def create_complex_markdown():
    """创建复杂的示例 Markdown 文件"""
    return """# 深度学习与自然语言处理

## 简介
深度学习在自然语言处理领域取得了革命性突破。本文将深入探讨这些技术的原理和应用。

### 历史发展
从早期的统计方法到现代的神经网络，NLP经历了多个发展阶段。

#### 统计时代
在深度学习出现之前，NLP主要依赖统计方法和规则系统。

#### 神经网络时代
随着计算能力的提升，神经网络开始在NLP中发挥重要作用。

## 核心技术

### 词嵌入技术
词嵌入是将词语映射到连续向量空间的技术。

#### Word2Vec
Word2Vec通过上下文预测来学习词向量。

#### GloVe
GloVe结合全局统计信息和局部上下文。

#### BERT嵌入
BERT引入了上下文相关的词表示。

### 序列模型
序列模型用于处理文本序列数据。

#### RNN/LSTM
循环神经网络及其变体LSTM和GRU。

#### Transformer
Transformer架构引入了注意力机制。

## 应用场景

### 机器翻译
神经机器翻译系统使用编码器-解码器架构。

### 文本生成
从GPT系列到最新的语言模型。

### 情感分析
分析文本的情感倾向和主观性。

## 技术挑战

### 计算资源
大规模模型需要大量计算资源。

### 数据质量
高质量训练数据的重要性。

### 模型解释性
深度学习模型的可解释性问题。

## 未来展望

### 多模态融合
结合文本、图像、语音的多模态理解。

### 小样本学习
在数据稀缺情况下的学习策略。

### 持续学习
模型随时间持续学习和适应的能力。

## 结论
深度学习在NLP领域的应用前景广阔，但仍面临诸多挑战需要解决。
"""

def demonstrate_parsing_methods():
    """演示不同的解析方法"""
    
    # 创建示例文件
    content = create_complex_markdown()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        parser = MarkdownParser()
        
        print("=== Markdown 章节解析演示 ===\n")
        
        # 1. 传统解析方法
        print("1. 传统元素解析:")
        traditional_docs = parser.parse(temp_file, source_type="file")
        print(f"   解析出 {len(traditional_docs)} 个文档")
        for i, doc in enumerate(traditional_docs[:3]):  # 只显示前3个
            print(f"   文档 {i+1}: {doc.metadata.get('type', 'unknown')} - {len(doc.page_content)} 字符")
        if len(traditional_docs) > 3:
            print(f"   ... 还有 {len(traditional_docs) - 3} 个文档")
        print()
        
        # 2. 章节解析方法
        print("2. 章节解析方法:")
        section_docs = parser.parse_with_sections(temp_file, source_type="file")
        print(f"   解析出 {len(section_docs)} 个章节")
        
        # 按层级分组显示
        level_counts = {}
        for doc in section_docs:
            level = doc.metadata['level']
            level_counts[level] = level_counts.get(level, 0) + 1
        
        for level in sorted(level_counts.keys()):
            indent = "  " * (level - 1) if level > 0 else ""
            print(f"   {indent}层级 {level}: {level_counts[level]} 个章节")
        
        print()
        
        # 显示详细章节信息
        print("3. 章节详细信息:")
        for i, doc in enumerate(section_docs):
            level = doc.metadata['level']
            title = doc.metadata['title']
            indent = "  " * (level - 1) if level > 0 else ""
            print(f"   {indent}#{i+1} [{level}] {title} ({len(doc.page_content)} 字符)")
        
        print()
        
        # 3. RAG Pipeline 对比
        print("4. RAG Pipeline 对比:")
        
        # 传统方式
        config_traditional = RAGConfig(
            chunk_size=500,
            chunk_overlap=50,
            parse_by_chapter=False
        )
        pipeline_traditional = RAGPipeline(config_traditional)
        chunks_traditional = pipeline_traditional.process_file(temp_file)
        
        # 章节方式
        config_chapter = RAGConfig(
            chunk_size=500,
            chunk_overlap=50,
            parse_by_chapter=True
        )
        pipeline_chapter = RAGPipeline(config_chapter)
        chunks_chapter = pipeline_chapter.process_file(temp_file)
        
        print(f"   传统方式: {len(chunks_traditional)} 个分块")
        print(f"   章节方式: {len(chunks_chapter)} 个分块")
        
        # 显示章节方式的元数据
        if chunks_chapter:
            print("   章节方式元数据示例:")
            sample_chunk = chunks_chapter[0]
            print(f"     标题: {sample_chunk['metadata'].get('title', 'N/A')}")
            print(f"     层级: {sample_chunk['metadata'].get('level', 'N/A')}")
            print(f"     文档索引: {sample_chunk['metadata'].get('document_index', 'N/A')}")
        
    finally:
        os.unlink(temp_file)

def demonstrate_use_cases():
    """演示不同使用场景"""
    
    print("\n=== 使用场景演示 ===\n")
    
    # 场景1: 学术论文
    academic_content = """# 基于Transformer的机器翻译研究

## 摘要
本文提出了一种改进的Transformer架构用于神经机器翻译任务。

## 1. 引言
机器翻译是NLP的重要任务之一...

## 2. 相关工作
### 2.1 传统方法
统计机器翻译方法...

### 2.2 神经方法
神经机器翻译的发展...

## 3. 方法
### 3.1 模型架构
我们提出的模型架构...

### 3.2 训练策略
训练策略的详细信息...

## 4. 实验
### 4.1 数据集
使用的数据集描述...

### 4.2 结果分析
实验结果的详细分析...

## 5. 结论
本文的贡献总结...
"""
    
    print("1. 学术论文场景:")
    parser = MarkdownParser()
    sections = parser.parse_by_sections(academic_content)
    
    print(f"   解析出 {len(sections)} 个章节")
    print("   章节结构:")
    for section in sections:
        level = section.metadata['level']
        title = section.metadata['title']
        indent = "  " * (level - 1) if level > 0 else ""
        print(f"   {indent}- {title}")
    
    # 场景2: 技术文档
    tech_doc = """# API文档

## 认证
### 基本认证
### OAuth认证

## 端点
### 用户相关
#### GET /users
#### POST /users
### 订单相关
#### GET /orders
#### POST /orders

## 错误处理
"""
    
    print("\n2. 技术文档场景:")
    sections = parser.parse_by_sections(tech_doc)
    print(f"   解析出 {len(sections)} 个章节")
    for section in sections:
        level = section.metadata['level']
        title = section.metadata['title']
        indent = "  " * (level - 1) if level > 0 else ""
        print(f"   {indent}- {title}")

def run_section_parsing_demo():
    """运行完整的章节解析演示"""
    demonstrate_parsing_methods()
    demonstrate_use_cases()

if __name__ == "__main__":
    run_section_parsing_demo()