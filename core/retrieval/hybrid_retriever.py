#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hybrid Retriever Module for RAG Core System

This module implements a hybrid retriever that combines vector retrieval and full-text retrieval.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from core.retrieval.base import RetrievalBase
from core.retrieval.vector_retriever import VectorRetriever
from core.retrieval.bm25_retriever import BM25Retriever
from core.embedding.base import EmbeddingBase
from utils.logger import get_module_logger
from conf.config import HybridRetrieverConfig


class HybridRetriever(RetrievalBase):
    """
    Hybrid retriever combining vector retrieval and full-text retrieval.
    
    This class implements a hybrid retrieval approach that combines:
    - Vector retrieval for semantic similarity
    - Full-text retrieval for keyword matching
    
    The final scores are weighted combinations of both methods.
    """
    
    def __init__(self, vector_retriever: VectorRetriever, bm25_retriever: BM25Retriever, config: Optional[HybridRetrieverConfig] = None):
        """
        Initialize hybrid retriever.
        
        Args:
            vector_retriever: Vector retriever instance for semantic search
            bm25_retriever: BM25 retriever instance for full-text search
            config: Hybrid retriever configuration
        """
        super().__init__()
        self.config = config or HybridRetrieverConfig()
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever
        self.logger = get_module_logger("HybridRetriever")
        
        self.logger.info("HybridRetriever initialized with BM25 support")
        self.logger.debug(f"Config: vector_weight={self.config.vector_weight}, "
                         f"text_weight={self.config.text_weight}, "
                         f"enable_text_search={self.config.enable_text_search}, "
                         f"enable_vector_search={self.config.enable_vector_search}")
    
    
    def search(self, query: str, top_k: int, score_threshold: float) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining vector and BM25 full-text retrieval.
        
        Args:
            query: Query text
            top_k: Number of results to return
            score_threshold: Minimum similarity score for results
            
        Returns:
            List of combined search results
        """
        results = []
        
        # Perform vector search
        vector_results = []
        if self.config.enable_vector_search:
            try:
                vector_results = self.vector_retriever.search(query, top_k * 2, score_threshold)
                self.logger.debug(f"Vector search returned {len(vector_results)} results")
                self.logger.debug(f"Vector search results top 5: {vector_results[:5]}")
            except Exception as e:
                self.logger.warning(f"Vector search failed: {e}")
        
        # Perform BM25 full-text search
        text_results = []
        if self.config.enable_text_search:
            try:
                text_results = self.bm25_retriever.search(query, top_k * 2, score_threshold)
                self.logger.debug(f"BM25 search returned {len(text_results)} results")
                self.logger.debug(f"BM25 search results top 5: {text_results[:5]}")
            except Exception as e:
                self.logger.warning(f"BM25 search failed: {e}")
        
        # Combine results
        combined_scores = {}
        
        # Process vector results
        for result in vector_results:
            text = result['text']
            score = result['score']
            # Normalize vector scores to 0-1 range
            normalized_score = min(score, 1.0)
            combined_scores[text] = {
                'text': text,
                'metadata': result.get('metadata', {}),
                'vector_score': normalized_score,
                'text_score': 0.0,
                'combined_score': normalized_score * self.config.vector_weight
            }
        
        # Process text results
        for result in text_results:
            text = result['text']
            score = result['score']
            # Normalize text scores to 0-1 range (BM25 scores can be > 1)
            normalized_score = min(score / 10.0, 1.0) if score > 1.0 else score
            
            if text in combined_scores:
                combined_scores[text]['text_score'] = normalized_score
                combined_scores[text]['combined_score'] += normalized_score * self.config.text_weight
            else:
                combined_scores[text] = {
                    'text': text,
                    'metadata': result.get('metadata', {}),
                    'vector_score': 0.0,
                    'text_score': normalized_score,
                    'combined_score': normalized_score * self.config.text_weight
                }
        
        # Sort by combined score
        sorted_results = sorted(
            combined_scores.values(),
            key=lambda x: x['combined_score'],
            reverse=True
        )
        
        # Limit to top_k results
        # final_results = sorted_results[:top_k]
        
        # Format results to match expected structure
        formatted_results = []
        for result in sorted_results:
            formatted_results.append({
                'text': result['text'],
                'metadata': result['metadata'],
                'score': result['combined_score'],
                'vector_score': result['vector_score'],
                'text_score': result['text_score']
            })
        
        self.logger.debug(f"Hybrid search completed: {len(formatted_results)} results")
        return formatted_results
    
    def update_config(self, **kwargs):
        """Update hybrid retriever configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                self.logger.info(f"Updated hybrid config: {key} = {value}")


class HybridRetrieverFactory:
    """Factory class for creating hybrid retriever instances."""
    
    @staticmethod
    def create_from_config(vector_retriever: VectorRetriever, config: dict = None) -> HybridRetriever:
        """
        Create hybrid retriever from configuration.
        
        Args:
            vector_retriever: Vector retriever instance
            config: Configuration dictionary
            
        Returns:
            HybridRetriever instance
        """
        if config is None:
            config = {}
        
        hybrid_config = HybridRetrieverConfig(
            vector_weight=config.get('vector_weight', 0.75),
            text_weight=config.get('text_weight', 0.25),
            enable_text_search=config.get('enable_text_search', True),
            enable_vector_search=config.get('enable_vector_search', True)
        )
        
        return HybridRetriever(vector_retriever, hybrid_config)