#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BM25 Retriever Module for RAG Core System

This module implements BM25-based full-text retrieval using Weaviate's BM25 search capabilities.
"""

from typing import List, Dict, Any, Optional
from core.retrieval.base import RetrievalBase
from core.vector.weaviate_vector import WeaviateVector
from utils.logger import get_module_logger


class BM25Retriever(RetrievalBase):
    """
    BM25-based full-text retriever using Weaviate's BM25 search.
    
    This class provides full-text search capabilities using the BM25 algorithm,
    which is particularly effective for keyword-based matching.
    """
    
    def __init__(self, vector_store: WeaviateVector):
        """
        Initialize BM25 retriever.
        
        Args:
            vector_store: WeaviateVector instance for accessing Weaviate's BM25 search
        """
        super().__init__()
        self.vector_store = vector_store
        self.logger = get_module_logger("BM25Retriever")
        
        self.logger.info("BM25Retriever initialized")
    
    def search(self, query: str, top_k: int = 5, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for documents using BM25 full-text search.
        
        Args:
            query: Query text for full-text search
            top_k: Number of results to return
            score_threshold: Minimum relevance score for results
            
        Returns:
            List of search results with text, metadata, and BM25 score
        """
        self.logger.debug(f"Starting BM25 search: query='{query[:50]}...', top_k={top_k}, score_threshold={score_threshold}")
        
        try:
            # Use Weaviate's BM25 full-text search
            results = self.vector_store.search_by_full_text(query, top_k, score_threshold)
            
            self.logger.debug(f"BM25 search completed: found {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"BM25 search failed: {e}")
            raise
    
    def search_by_text(self, query: str, top_k: int = 5, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Alias for search method to maintain consistency with other retrievers.
        
        Args:
            query: Query text
            top_k: Number of results to return
            score_threshold: Minimum relevance score for results
            
        Returns:
            List of search results
        """
        return self.search(query, top_k, score_threshold)
    
    def update_index(self):
        """
        Update the index if needed.
        
        Note: Weaviate handles index updates automatically when new documents are added,
        so this method is mainly for interface consistency.
        """
        self.logger.debug("BM25 index update requested (Weaviate handles this automatically)")
        pass