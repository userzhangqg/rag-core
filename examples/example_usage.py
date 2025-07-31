#!/usr/bin/env python3
"""
RAG流程使用示例

演示如何使用RAGPipeline处理markdown文件和内容
"""

import os
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.pipeline.rag_pipeline import RAGPipeline, RAGPipelineBuilder


rag_pipeline = RAGPipelineBuilder.create_default_pipeline()
def create_sample_markdown():
    """创建示例markdown文件"""
    content = """
# 机器学习基础

## 什么是机器学习

机器学习是人工智能的一个分支，它使计算机系统能够从数据中自动学习和改进，而无需明确编程。

### 主要类型

1. **监督学习**
   - 分类
   - 回归

2. **无监督学习**
   - 聚类
   - 降维

3. **强化学习**
   - 智能体与环境交互
   - 奖励机制

## 常用算法

### 线性回归
线性回归是一种基本的监督学习算法，用于预测连续值输出。

公式：
```
y = wx + b
```

### 决策树
决策树通过一系列if-else条件来进行分类或回归。

优点：
- 易于理解和解释
- 可以处理数值和类别数据
- 不需要太多的数据准备

缺点：
- 容易过拟合
- 对连续值的处理不够好

## 实际应用

机器学习在各个领域都有广泛应用：

| 领域 | 应用示例 |
|------|----------|
| 医疗 | 疾病诊断、药物发现 |
| 金融 | 风险评估、欺诈检测 |
| 交通 | 自动驾驶、路线优化 |
| 零售 | 推荐系统、需求预测 |

## 总结

机器学习正在改变我们生活的方方面面，从智能手机到自动驾驶汽车，其影响力无处不在。
"""
    
    # 创建临时文件
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8')
    temp_file.write(content)
    temp_file.close()
    
    return temp_file.name


def main():
    """主函数"""
    print("=== RAG流程使用示例 ===\n")
    
    # 创建RAG管道
    pipeline = RAGPipeline()
    
    # 示例1: 处理文件
    print("1. 处理单个markdown文件")
    sample_file = create_sample_markdown()
    
    try:
        chunks = pipeline.process_file(sample_file)
        print(f"   生成了 {len(chunks)} 个文本分块")
        
        # 显示前几个分块
        for i, chunk in enumerate(chunks[:3]):
            print(f"   分块 {i+1}: {len(chunk['text'])} 字符")
            print(f"   预览: {chunk['text'][:100]}...")
            print()
    
    finally:
        # 清理临时文件
        os.unlink(sample_file)
    
    # 示例2: 处理文本内容
    print("2. 处理文本内容")
    content = """
    # Python基础
    
    Python是一种解释型、高级、通用的编程语言。
    
    ## 特点
    - 简单易学
    - 功能强大
    - 社区活跃
    """
    
    chunks = pipeline.process_content(content, source_name="python_tutorial")
    print(f"   生成了 {len(chunks)} 个文本分块")
    
    # 示例3: 使用不同配置
    print("3. 使用学术文档配置")
    academic_pipeline = RAGPipelineBuilder.create_academic_pipeline()
    chunks = academic_pipeline.process_content(content, source_name="academic_doc")
    print(f"   学术配置生成了 {len(chunks)} 个分块")
    
    # 示例4: 批量处理
    print("4. 管道配置信息")
    info = pipeline.get_pipeline_info()
    print(f"   分块大小: {info['chunker_config']['chunk_size']}")
    print(f"   重叠大小: {info['chunker_config']['chunk_overlap']}")
    print(f"   分隔符: {info['chunker_config']['separators']}")


if __name__ == "__main__":
    main()