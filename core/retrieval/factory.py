#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Retrieval Factory Module for RAG Core System
"""

from typing import Optional, Dict, Any
from core.retrieval.base import RetrievalBase
from core.retrieval.vector_retriever import VectorRetriever
from core.retrieval.bm25_retriever import BM25Retriever
from core.retrieval.hybrid_retriever import HybridRetriever
from core.vector.base import VectorBase


class RetrievalFactory:
    """Factory class for creating retrieval instances based on configuration."""
    
    @staticmethod
    def create_retriever(
        retriever_type: str = "vector",
        vector_store: Optional[VectorBase] = None,
        hybrid_config: Optional[Dict[str, Any]] = None
    ) -> RetrievalBase:
        """
        Create a retriever instance based on the type.
        
        Args:
            retriever_type: Retriever type ("vector", "bm25", "hybrid")
            vector_store: Vector store instance
            hybrid_config: Configuration for hybrid retriever
            
        Returns:
            RetrievalBase: Retriever instance
        
        Raises:
            ValueError: If the retriever type is not supported
            ValueError: If required parameters are missing
        """
        if retriever_type == "vector":
            if vector_store is None:
                raise ValueError("vector_store is required for vector retriever")
            return VectorRetriever(vector_store)
            
        elif retriever_type == "text":
            if vector_store is None:
                raise ValueError("vector_store is required for bm25 retriever")
            return BM25Retriever(vector_store)
            
        elif retriever_type == "hybrid":
            if vector_store is None:
                raise ValueError("vector_store is required for hybrid retriever")
            if hybrid_config is None:
                hybrid_config = {"vector_weight": 0.7, "text_weight": 0.3}
            
            vector_retriever = VectorRetriever(vector_store)
            bm25_retriever = BM25Retriever(vector_store)
            return HybridRetriever(vector_retriever, bm25_retriever, hybrid_config)
            
        else:
            raise ValueError(f"Unsupported retriever type: {retriever_type}")