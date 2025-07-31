#!/usr/bin/env python3
"""
测试脚本：验证parser模块的日志功能
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tempfile

from utils.logger import setup_logger
from core.parser.markdown_parser import MarkdownParser



def create_test_markdown():
    """创建测试markdown内容"""
    return """# 机器学习基础

## 引言
机器学习是人工智能的一个分支，专注于让计算机系统能够从数据中学习并改进性能，而无需进行显式编程。

### 历史背景
机器学习的发展可以追溯到20世纪50年代，经历了多个重要阶段。

## 主要算法类型

### 监督学习
监督学习使用标记数据来训练模型。

#### 线性回归
线性回归是最基础的监督学习算法之一。

## 总结
机器学习正在改变我们生活的方方面面。
"""

def test_parser_logging():
    """测试parser模块的日志功能"""
    print("=== 测试Parser模块日志功能 ===\n")
    
    # 设置日志
    setup_logger()
    
    # 创建parser实例
    parser = MarkdownParser(remove_hyperlinks=False, remove_images=False)
    
    # 测试1: 基础解析
    print("1. 测试基础解析功能...")
    content = create_test_markdown()
    documents = parser.parse(content, source_type="content")
    print(f"   解析完成，生成 {len(documents)} 个文档\n")
    
    # 测试2: 章节解析
    print("2. 测试章节解析功能...")
    sections = parser.parse_by_sections(content)
    print(f"   章节解析完成，生成 {len(sections)} 个章节\n")
    
    # 测试3: 文件解析
    print("3. 测试文件解析功能...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        documents = parser.parse(tmp_file_path, source_type="file")
        print(f"   文件解析完成，生成 {len(documents)} 个文档\n")
    finally:
        os.unlink(tmp_file_path)

if __name__ == "__main__":
    test_parser_logging()