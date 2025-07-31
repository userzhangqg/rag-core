#!/usr/bin/env python3
"""
按章节解析 Markdown 的示例脚本

演示如何使用 MarkdownParser 的 parse_with_sections 方法按标题章节解析 Markdown 内容
"""

import os
import tempfile
from core.parser.markdown_parser import MarkdownParser

def create_sample_markdown():
    """创建示例 Markdown 文件"""
    sample_content = """# 机器学习基础

## 引言
机器学习是人工智能的一个分支，专注于让计算机系统能够从数据中学习并改进性能，而无需进行显式编程。

### 历史背景
机器学习的发展可以追溯到20世纪50年代，经历了多个重要阶段。

## 主要算法类型

### 监督学习
监督学习使用标记数据来训练模型。

#### 线性回归
线性回归是最基础的监督学习算法之一。

#### 决策树
决策树通过一系列条件判断来进行分类或回归。

### 无监督学习
无监督学习处理未标记的数据。

## 应用领域
机器学习在各个领域都有广泛应用，包括：

- 计算机视觉
- 自然语言处理
- 推荐系统
- 医疗诊断

## 总结
机器学习正在改变我们生活的方方面面。
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(sample_content)
        return f.name

def main():
    """主函数"""
    parser = MarkdownParser(remove_hyperlinks=False, remove_images=False)
    
    # 创建示例文件
    sample_file = create_sample_markdown()
    
    try:
        print("=== 按章节解析 Markdown 示例 ===\n")
        
        # 方法1: 解析文件
        print("1. 解析文件路径:")
        sections = parser.parse_with_sections(sample_file, source_type="file")
        
        print(f"共解析出 {len(sections)} 个章节:\n")
        for i, section in enumerate(sections, 1):
            print(f"章节 {i}:")
            print(f"  标题: {section.metadata['title']}")
            print(f"  层级: {section.metadata['level']}")
            print(f"  行号: {section.metadata['header_line']}")
            print(f"  内容长度: {len(section.page_content)} 字符")
            print(f"  内容预览: {section.page_content[:100]}...")
            print()
        
        # 方法2: 解析内容字符串
        print("2. 解析内容字符串:")
        content = """# 深度学习

## 神经网络基础
神经网络是深度学习的基础。

### 感知机
感知机是最简单的神经网络单元。

## 卷积神经网络
CNN 在图像处理中表现出色。
"""
        
        sections = parser.parse_with_sections(content, source_type="content")
        print(f"共解析出 {len(sections)} 个章节:\n")
        for section in sections:
            print(f"标题: {section.metadata['title']} (层级 {section.metadata['level']})")
        
        # 方法3: 解析无标题内容
        print("\n3. 解析无标题内容:")
        no_header_content = "这是一个没有标题的文档。\n\n这是第二段内容。"
        sections = parser.parse_with_sections(no_header_content, source_type="content")
        print(f"无标题内容解析出 {len(sections)} 个章节:")
        for section in sections:
            print(f"标题: {section.metadata['title']} (默认)")
        
        # 方法4: 使用原始解析方法对比
        print("\n4. 与原始解析方法对比:")
        original_docs = parser.parse(sample_file, source_type="file")
        print(f"原始方法解析出 {len(original_docs)} 个文档")
        print(f"章节方法解析出 {len(sections)} 个章节")
        
    finally:
        # 清理临时文件
        os.unlink(sample_file)

if __name__ == "__main__":
    main()