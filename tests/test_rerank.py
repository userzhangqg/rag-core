#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test cases for Rerank functionality in RAG Pipeline
"""

import pytest
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.pipeline.rag_pipeline import RAGPipeline
from core.reranker.factory import RerankerFactory


class TestRerank:
    """Test cases for Rerank functionality."""
    
    def setup_method(self):
        """Set up test resources."""
        # Create RAGPipeline instance
        self.pipeline = RAGPipeline()
    
    def test_reranker_initialization(self):
        """Test reranker initialization."""
        # Check that reranker is initialized
        assert self.pipeline.reranker is not None
        
        # Check that reranker is of the correct type
        from core.reranker.local_api_reranker import LocalAPIReranker
        assert isinstance(self.pipeline.reranker, LocalAPIReranker)
    
    def test_rerank_functionality(self):
        """Test rerank functionality."""
        # Create test data
        query = "人工智能的发展历程"
        documents = [
            "人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。",
            "机器学习是人工智能的一个分支，它使计算机能够从数据中学习并做出决策或预测。",
            "深度学习是机器学习的一个子集，它模仿人脑的工作方式处理数据和创建模式，用于决策制定。",
            "自然语言处理是人工智能的一个分支，它帮助计算机理解和解释人类语言。"
        ]
        
        # Test rerank functionality
        reranked_docs = self.pipeline.reranker.rerank(query, documents)
        
        # Check that the reranked documents are returned
        assert reranked_docs is not None
        assert isinstance(reranked_docs, list)
        assert len(reranked_docs) == len(documents)
    
    def test_query_with_rerank(self):
        """Test query with rerank functionality."""
        # Create test data
        query = "人工智能的发展历程"
        # Mock retrieved documents
        self.pipeline.retriever.search = lambda q, k, s: [
            {'text': "人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。"},
            {'text': "机器学习是人工智能的一个分支，它使计算机能够从数据中学习并做出决策或预测。"},
            {'text': "深度学习是机器学习的一个子集，它模仿人脑的工作方式处理数据和创建模式，用于决策制定。"},
            {'text': "自然语言处理是人工智能的一个分支，它帮助计算机理解和解释人类语言。"}
        ]
        
        # Mock LLM generate method
        original_generate = self.pipeline.llm.generate
        self.pipeline.llm.generate = lambda prompt: "这是一个人工智能发展历程的回答。"
        
        # Test query with rerank enabled
        response = self.pipeline.query(query, top_k=5, use_rerank=True)
        
        # Check that a response is returned
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Restore original LLM generate method
        self.pipeline.llm.generate = original_generate
    
    def test_query_without_rerank(self):
        """Test query without rerank functionality."""
        # Create test data
        query = "人工智能的发展历程"
        # Mock retrieved documents
        self.pipeline.retriever.search = lambda q, k, s: [
            {'text': "人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。"},
            {'text': "机器学习是人工智能的一个分支，它使计算机能够从数据中学习并做出决策或预测。"},
            {'text': "深度学习是机器学习的一个子集，它模仿人脑的工作方式处理数据和创建模式，用于决策制定。"},
            {'text': "自然语言处理是人工智能的一个分支，它帮助计算机理解和解释人类语言。"}
        ]
        
        # Mock LLM generate method
        original_generate = self.pipeline.llm.generate
        self.pipeline.llm.generate = lambda prompt: "这是一个人工智能发展历程的回答。"
        
        # Test query with rerank disabled
        response = self.pipeline.query(query, top_k=5, use_rerank=False)
        
        # Check that a response is returned
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Restore original LLM generate method
        self.pipeline.llm.generate = original_generate
    
    def test_reranker_factory(self):
        """Test reranker factory functionality."""
        # Test creating LocalAPIReranker
        reranker = RerankerFactory.create_reranker("local_api")
        from core.reranker.local_api_reranker import LocalAPIReranker
        assert isinstance(reranker, LocalAPIReranker)
        
        # Test creating reranker with unsupported provider
        with pytest.raises(ValueError):
            RerankerFactory.create_reranker("unsupported_provider")