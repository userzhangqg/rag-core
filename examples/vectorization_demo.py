#!/usr/bin/env python3
"""
向量化功能使用示例

演示如何使用RAGPipeline的向量化功能
"""

import os
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.pipeline.rag_pipeline import RAGPipeline, RAGPipelineBuilder


def create_sample_markdown():
    """创建示例markdown文件"""
    content = """
# 人工智能简介

## 什么是人工智能

人工智能（Artificial Intelligence），英文缩写为AI。它是研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统的一门新的技术科学。

### 发展历程

1. **起步阶段（1956年以前）**
   - 主要孕育了人工智能的基本思想
   - 形成了若干重要的理论和方法

2. **形成阶段（1956-1970年）**
   - 达特茅斯会议标志着人工智能学科的诞生
   - 出现了第一批人工智能程序

3. **发展与低谷阶段（1970-1980年）**
   - 专家系统的兴起
   - 遇到了第一次人工智能寒冬

## 主要应用领域

### 机器学习
机器学习是实现人工智能的一种方法，也是人工智能的核心。

### 自然语言处理
自然语言处理是计算机科学领域与人工智能领域中的一个重要方向。

### 计算机视觉
计算机视觉是一门研究如何使机器"看"的科学。

## 未来展望

人工智能的未来充满无限可能，将在更多领域发挥重要作用。
"""
    
    # 创建临时文件
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8')
    temp_file.write(content)
    temp_file.close()
    
    return temp_file.name


def main():
    """主函数"""
    print("=== 向量化功能使用示例 ===\n")
    
    # 创建RAG管道
    pipeline = RAGPipeline()
    
    # 处理文件并自动向量化
    print("1. 处理文件并自动向量化")
    sample_file = create_sample_markdown()
    
    try:
        chunks = pipeline.process_file(sample_file)
        print(f"   生成了 {len(chunks)} 个文本分块")
        print(f"   向量化完成: {len(chunks)}个文本已存储到向量数据库")
        
        # 显示前几个分块
        for i, chunk in enumerate(chunks[:2]):
            print(f"   分块 {i+1}: {len(chunk['text'])} 字符")
            print(f"   预览: {chunk['text'][:100]}...")
            print()
    
    finally:
        # 清理临时文件
        os.unlink(sample_file)
    
    # 处理文本内容并自动向量化
    print("2. 处理文本内容并自动向量化")
    content = """
    # 深度学习基础
    
    深度学习是机器学习的一个子集，它模仿人脑的工作方式来处理数据和创建模式，用于决策制定。
    
    ## 神经网络
    神经网络是深度学习的基础，由输入层、隐藏层和输出层组成。
    """
    
    chunks = pipeline.process_content(content, source_name="deep_learning")
    print(f"   生成了 {len(chunks)} 个文本分块")
    print(f"   向量化完成: {len(chunks)}个文本已存储到向量数据库")


if __name__ == "__main__":
    main()