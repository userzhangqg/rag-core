#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
本地API Embedding演示

展示如何使用本地API Embedding方式
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.embedding.local_api_embedding import LocalAPIEmbedding
from core.pipeline.rag_pipeline import RAGPipeline, RAGConfig


def demo_local_api_embedding():
    """演示本地API Embedding的使用"""
    print("=== 本地API Embedding演示 ===")
    
    # 初始化本地API Embedding
    # 注意：这里使用示例URL，实际使用时请替换为真实的本地API地址
    embedding = LocalAPIEmbedding(api_url="http://172.16.89.10:10669/scbllm/embedding-infer/embedding")
    
    # 测试文本
    test_text = "这是一个使用本地API生成嵌入向量的示例文本"
    
    try:
        # 生成嵌入向量
        embedding_vector = embedding.embed_text(test_text)
        print(f"文本: {test_text}")
        print(f"嵌入向量维度: {len(embedding_vector)}")
        print(f"嵌入向量前5个元素: {embedding_vector[:5]}")
        
        # 测试多文本嵌入
        texts = [
            "第一个测试文本",
            "第二个测试文本",
            "第三个测试文本"
        ]
        
        embedding_vectors = embedding.embed_documents(texts)
        print(f"\n多文本嵌入结果:")
        for i, (text, vec) in enumerate(zip(texts, embedding_vectors)):
            print(f"  文本 {i+1}: {text}")
            print(f"    向量维度: {len(vec)}")
    except Exception as e:
        print(f"本地API Embedding调用失败: {e}")


def demo_rag_with_local_api():
    """演示使用本地API Embedding的RAG流程"""
    print("\n=== 使用本地API Embedding的RAG流程演示 ===")
    
    # 配置RAG使用本地API Embedding
    config = RAGConfig(
        embedding_provider="local_api",
        embedding_api_url="http://172.16.89.10:10669/scbllm/embedding-infer/embedding",
        vector_db_url="http://172.28.86.42:28080"
    )
    
    # 初始化RAG管道
    rag = RAGPipeline(config=config)
    
    # 测试内容
    content = "# 示例文档\n\n这是一个使用本地API Embedding的RAG流程示例。\n\n## 章节一\n\n这是第一章的内容。\n\n## 章节二\n\n这是第二章的内容。"
    
    try:
        # 处理内容
        chunks = rag.process_content(content, source_name="example.md")
        print(f"内容处理完成，生成了 {len(chunks)} 个文本块")
        
        # 显示部分结果
        for i, chunk in enumerate(chunks[:3]):  # 只显示前3个块
            print(f"\n文本块 {i+1}:")
            print(f"  内容: {chunk['text'][:100]}...")
            print(f"  元数据: {chunk['metadata']}")
    except Exception as e:
        import traceback
        print(f"RAG流程处理失败: {e}")
        traceback.print_exc()


def main():
    """主函数"""
    print("本地API Embedding使用演示")
    print("=" * 50)
    
    # 演示本地API Embedding
    demo_local_api_embedding()
    
    # 演示使用本地API Embedding的RAG流程
    demo_rag_with_local_api()
    
    print("\n演示完成")


if __name__ == "__main__":
    main()