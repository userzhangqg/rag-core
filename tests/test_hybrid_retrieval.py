#!/usr/bin/env python3
"""
测试混合检索功能的脚本
"""
import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.pipeline.rag_pipeline import RAGPipeline
from conf.config import RAGConfig

def test_hybrid_retrieval():
    """测试混合检索功能"""
    
    print("=== 测试混合检索功能 ===")
    
    # 创建配置
    config = RAGConfig.from_config_file()
    
    # 初始化RAG管道
    rag_pipeline = RAGPipeline(config)
    
    # 测试查询
    test_query = "什么是机器学习"
    
    print(f"测试查询: {test_query}")
    
    # 测试不同检索方式
    retrieval_types = ["hybrid", "vector", "text"]
    
    for retrieval_type in retrieval_types:
        print(f"\n--- 使用 {retrieval_type} 检索 ---")
        try:
            # 临时修改配置
            config.retrieval_type = retrieval_type
            
            # 重新初始化检索器
            rag_pipeline.retriever = None  # 强制重新初始化
            
            # 执行查询
            results = rag_pipeline.query(
                query_text=test_query,
                top_k=5,
                search_type=retrieval_type
            )
            
            print(f"检索成功，返回结果长度: {len(results) if isinstance(results, list) else 'N/A'}")
            print(f"结果预览: {results[:200] if isinstance(results, str) else '结果格式正确'}")
            
        except Exception as e:
            print(f"{retrieval_type} 检索失败: {str(e)}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(level=logging.INFO)
    
    test_hybrid_retrieval()