#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Weaviate Vectorization Demo
演示如何使用SiliconFlowEmbedding和WeaviateVector进行文本向量化和向量搜索
"""

import sys
import os
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.embedding.sijiblob_embedding import SiliconFlowEmbedding
from core.vector.weaviate_vector import WeaviateVector


def demo_embedding():
    """演示文本向量化功能"""
    print("=== 文本向量化演示 ===")
    
    # 初始化嵌入模型
    # 注意：需要设置有效的硅基流动API密钥
    embedding = SiliconFlowEmbedding(api_key="your_api_key_here", model_name="BAAI/bge-large-zh-v1.5")
    
    # 测试文档向量化
    documents = [
        "机器学习是人工智能的一个分支，它使计算机能够从数据中学习。",
        "深度学习是机器学习的一个子领域，它使用神经网络来模拟人脑的工作方式。",
        "自然语言处理是计算机科学和人工智能的一个分支，它关注计算机与人类语言的交互。"
    ]
    
    print("1. 文档向量化:")
    doc_embeddings = embedding.embed_documents(documents)
    print(f"   成功生成 {len(doc_embeddings)} 个文档的嵌入向量")
    print(f"   第一个文档的嵌入维度: {len(doc_embeddings[0])}")
    
    # 测试查询向量化
    query = "什么是人工智能？"
    print(f"\n2. 查询向量化:")
    query_embedding = embedding.embed_query(query)
    print(f"   查询文本: {query}")
    print(f"   查询嵌入维度: {len(query_embedding)}")
    
    print("\n" + "="*50 + "\n")


def demo_vector_store():
    """演示向量存储和搜索功能"""
    print("=== 向量存储和搜索演示 ===")
    
    # 初始化嵌入模型
    # 注意：需要设置有效的硅基流动API密钥
    embedding = SiliconFlowEmbedding(api_key="your_api_key_here", model_name="BAAI/bge-large-zh-v1.5")
    
    # 初始化向量存储
    vector_store = WeaviateVector.from_config(
        embedding_model=embedding,
        index_name="RAGDemoIndex"
    )
    
    # 存储文本
    texts = [
        "机器学习是人工智能的一个分支，它使计算机能够从数据中学习。",
        "深度学习是机器学习的一个子领域，它使用神经网络来模拟人脑的工作方式。",
        "自然语言处理是计算机科学和人工智能的一个分支，它关注计算机与人类语言的交互。",
        "计算机视觉是人工智能的一个领域，它使计算机能够理解和处理图像和视频。",
        "强化学习是一种机器学习方法，其中智能体通过与环境交互来学习。"
    ]
    
    print("1. 存储文本到向量数据库:")
    node_ids = vector_store.store_texts(texts)
    print(f"   成功存储 {len(node_ids)} 个文本")
    print(f"   节点IDs: {node_ids}")
    
    # 搜索相似文本
    query = "人工智能的分支有哪些？"
    print(f"\n2. 搜索相似文本:")
    print(f"   查询: {query}")
    results = vector_store.search(query, top_k=3)
    print(f"   找到 {len(results)} 个相似文本:")
    
    for i, result in enumerate(results, 1):
        print(f"   {i}. 文本: {result['text'][:100]}...")
        print(f"      相似度得分: {result['score']:.4f}")
        print(f"      元数据: {result['metadata']}")
    
    # 使用向量进行搜索
    print(f"\n3. 使用向量进行搜索:")
    query_vector = embedding.embed_query("机器学习和深度学习有什么区别？")
    vector_results = vector_store.search_by_vector(query_vector, top_k=3)
    print(f"   找到 {len(vector_results)} 个相似文本:")
    
    for i, result in enumerate(vector_results, 1):
        print(f"   {i}. 文本: {result['text'][:100]}...")
        print(f"      相似度得分: {result['score']:.4f}")
    
    print("\n" + "="*50 + "\n")


def demo_embedding_with_provider(provider: str = "siliconflow"):
    """演示使用不同提供商的文本向量化功能"""
    print(f"=== {provider}文本向量化演示 ===")
    
    # 初始化嵌入模型
    if provider == "siliconflow":
        # 注意：需要设置有效的硅基流动API密钥
        embedding = SiliconFlowEmbedding(api_key="your_api_key_here", model_name="BAAI/bge-large-zh-v1.5")
    elif provider == "llama":
        embedding = LlamaEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    else:
        raise ValueError(f"不支持的Embedding提供商: {provider}")
    
    # 测试文档向量化
    documents = [
        "机器学习是人工智能的一个分支，它使计算机能够从数据中学习。",
        "深度学习是机器学习的一个子领域，它使用神经网络来模拟人脑的工作方式。",
        "自然语言处理是计算机科学和人工智能的一个分支，它关注计算机与人类语言的交互。"
    ]
    
    print("1. 文档向量化:")
    doc_embeddings = embedding.embed_documents(documents)
    print(f"   成功生成 {len(doc_embeddings)} 个文档的嵌入向量")
    print(f"   第一个文档的嵌入维度: {len(doc_embeddings[0])}")
    
    # 测试查询向量化
    query = "什么是人工智能？"
    print(f"\n2. 查询向量化:")
    query_embedding = embedding.embed_query(query)
    print(f"   查询文本: {query}")
    print(f"   查询嵌入维度: {len(query_embedding)}")
    
    print("\n" + "="*50 + "\n")


def demo_vector_store_with_provider(provider: str = "siliconflow"):
    """演示使用不同提供商的向量存储和搜索功能"""
    print(f"=== {provider}向量存储和搜索演示 ===")
    
    # 初始化嵌入模型
    if provider == "siliconflow":
        # 注意：需要设置有效的硅基流动API密钥
        embedding = SiliconFlowEmbedding(api_key="your_api_key_here", model_name="BAAI/bge-large-zh-v1.5")
    elif provider == "llama":
        embedding = LlamaEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    else:
        raise ValueError(f"不支持的Embedding提供商: {provider}")
    
    # 初始化向量存储
    vector_store = WeaviateVector.from_config(
        embedding_model=embedding,
        index_name="RAGDemoIndex"
    )
    
    # 存储文本
    texts = [
        "机器学习是人工智能的一个分支，它使计算机能够从数据中学习。",
        "深度学习是机器学习的一个子领域，它使用神经网络来模拟人脑的工作方式。",
        "自然语言处理是计算机科学和人工智能的一个分支，它关注计算机与人类语言的交互。",
        "计算机视觉是人工智能的一个领域，它使计算机能够理解和处理图像和视频。",
        "强化学习是一种机器学习方法，其中智能体通过与环境交互来学习。"
    ]
    
    print("1. 存储文本到向量数据库:")
    node_ids = vector_store.store_texts(texts)
    print(f"   成功存储 {len(node_ids)} 个文本")
    print(f"   节点IDs: {node_ids}")
    
    # 搜索相似文本
    query = "人工智能的分支有哪些？"
    print(f"\n2. 搜索相似文本:")
    print(f"   查询: {query}")
    results = vector_store.search(query, top_k=3)
    print(f"   找到 {len(results)} 个相似文本:")
    
    for i, result in enumerate(results, 1):
        print(f"   {i}. 文本: {result['text'][:100]}...")
        print(f"      相似度得分: {result['score']:.4f}")
        print(f"      元数据: {result['metadata']}")
    
    # 使用向量进行搜索
    print(f"\n3. 使用向量进行搜索:")
    query_vector = embedding.embed_query("机器学习和深度学习有什么区别？")
    vector_results = vector_store.search_by_vector(query_vector, top_k=3)
    print(f"   找到 {len(vector_results)} 个相似文本:")
    
    for i, result in enumerate(vector_results, 1):
        print(f"   {i}. 文本: {result['text'][:100]}...")
        print(f"      相似度得分: {result['score']:.4f}")
    
    print("\n" + "="*50 + "\n")


def main():
    """主函数"""
    print("Weaviate向量化模块演示\n")
    
    # 演示使用不同提供商的文本向量化
    demo_embedding_with_provider("siliconflow")
    demo_embedding_with_provider("llama")
    
    # 演示使用不同提供商的向量存储和搜索
    # 注意：这需要Weaviate服务正在运行
    try:
        demo_vector_store_with_provider("siliconflow")
        demo_vector_store_with_provider("llama")
    except Exception as e:
        print(f"向量存储演示失败: {e}")
        print("请确保Weaviate服务正在运行在 http://localhost:8080")


if __name__ == "__main__":
    main()