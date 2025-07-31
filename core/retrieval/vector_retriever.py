#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vector Retriever Module for RAG Core System
"""

from typing import List, Dict, Any, Optional
from core.retrieval.base import RetrievalBase
from core.vector.weaviate_vector import WeaviateVector


class VectorRetriever(RetrievalBase):
    """Vector-based retriever implementation using Weaviate."""
    
    def __init__(self, vector_store: WeaviateVector):
        """
        Initialize the VectorRetriever.
        
        Args:
            vector_store: WeaviateVector instance to use for retrieval
        """
        super().__init__()
        self.vector_store = vector_store
        self.logger.debug(f"Initialized VectorRetriever with vector store: {type(vector_store).__name__}")
    
    def search(self, query: str, top_k: int = 5, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for documents based on the query using vector similarity.
        
        Args:
            query: Query text
            top_k: Number of results to return
            score_threshold: Minimum similarity score for results
            
        Returns:
            List of search results with text, metadata, and similarity score
        """
        self.logger.debug(f"Starting vector search: query='{query[:50]}...', top_k={top_k}, score_threshold={score_threshold}")
        
        results = self.vector_store.search(query, top_k, score_threshold)
        
        self.logger.debug(f"Vector search completed: found {len(results)} results")
        if results:
            self.logger.debug(f"Top result score: {results[0].get('score', 'N/A')}")
        
        return results