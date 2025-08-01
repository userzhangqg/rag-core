#!/usr/bin/env python3
"""
测试BM25全文检索和混合检索功能的脚本
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from core.pipeline.rag_pipeline import RAGPipeline
from core.retrieval.bm25_retriever import BM25Retriever
from core.retrieval.vector_retriever import VectorRetriever
from conf.config import RAGConfig

def test_bm25_and_hybrid():
    """测试BM25全文检索和混合检索功能"""
    
    print("=== 测试BM25全文检索和混合检索功能 ===")
    
    # 创建配置
    config = RAGConfig.from_config_file()
    
    # 初始化RAG管道
    rag_pipeline = RAGPipeline(config)
    
    # 测试查询
    test_queries = [
        "机器学习",
        "深度学习",
        "人工智能应用",
        "神经网络训练"
    ]
    
    for test_query in test_queries:
        print(f"\n--- 测试查询: {test_query} ---")
        
        # 测试不同检索方式
        retrieval_types = ["vector", "text", "hybrid"]
        
        for retrieval_type in retrieval_types:
            try:
                print(f"\n{retrieval_type.upper()} 检索结果:")
                
                # 临时修改配置
                config.retrieval_type = retrieval_type
                
                # 重新初始化检索器
                vector_retriever = VectorRetriever(rag_pipeline.vector_store)
                bm25_retriever = BM25Retriever(rag_pipeline.vector_store)
                
                from core.retrieval.hybrid_retriever import HybridRetriever
                
                if retrieval_type == "hybrid":
                    retriever = HybridRetriever(vector_retriever, bm25_retriever, config.hybrid_config)
                elif retrieval_type == "vector":
                    retriever = vector_retriever
                elif retrieval_type == "text":
                    retriever = bm25_retriever
                
                # 执行检索
                results = retriever.search(test_query, top_k=3, score_threshold=0)
                
                print(f"  找到 {len(results)} 个结果")
                for i, result in enumerate(results[:3], 1):
                    score = result.get('score', 0)
                    text_preview = result['text'][:100] + "..." if len(result['text']) > 100 else result['text']
                    print(f"  {i}. 分数: {score:.4f}")
                    print(f"     内容: {text_preview}")
                    
            except Exception as e:
                print(f"  {retrieval_type} 检索失败: {str(e)}")
    
    print("\n=== 测试完成 ===")

def test_individual_retrievers():
    """单独测试BM25Retriever和VectorRetriever"""
    
    print("\n=== 单独测试检索器 ===")
    
    config = RAGConfig.from_config_file()
    rag_pipeline = RAGPipeline(config)
    
    # 测试BM25Retriever
    print("\n--- 测试 BM25Retriever ---")
    bm25_retriever = BM25Retriever(rag_pipeline.vector_store)
    
    try:
        results = bm25_retriever.search("机器学习", top_k=3)
        print(f"BM25检索成功，找到 {len(results)} 个结果")
        for i, result in enumerate(results[:2], 1):
            print(f"  {i}. BM25分数: {result['score']:.4f}")
    except Exception as e:
        print(f"BM25检索失败: {str(e)}")
    
    # 测试VectorRetriever
    print("\n--- 测试 VectorRetriever ---")
    vector_retriever = VectorRetriever(rag_pipeline.vector_store)
    
    try:
        results = vector_retriever.search("机器学习", top_k=3)
        print(f"向量检索成功，找到 {len(results)} 个结果")
        for i, result in enumerate(results[:2], 1):
            print(f"  {i}. 向量相似度: {result['score']:.4f}")
    except Exception as e:
        print(f"向量检索失败: {str(e)}")

if __name__ == "__main__":
    # 确保有测试数据
    print("请确保系统中已有测试数据，或先运行文档处理流程")
    
    test_individual_retrievers()
    test_bm25_and_hybrid()