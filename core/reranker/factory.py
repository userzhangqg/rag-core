#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reranker Factory Module for RAG Core System
"""

from typing import Optional
from core.reranker.base import RerankerBase
from core.reranker.local_api_reranker import LocalAPIReranker


class RerankerFactory:
    """Factory class for creating reranker instances based on configuration."""
    
    @staticmethod
    def create_reranker(provider: str = "local_api",
                        api_url: Optional[str] = None) -> RerankerBase:
        """
        Create a reranker instance based on the provider.
        
        Args:
            provider: Reranker provider name (e.g., "local_api")
            api_url: API URL for the reranker service
            
        Returns:
            RerankerBase: Reranker instance
        
        Raises:
            ValueError: If the provider is not supported
        """
        if provider == "local_api":
            return LocalAPIReranker(api_url=api_url or "http://172.16.89.10:10669/scbllm/embedding-infer/reranker")
        else:
            raise ValueError(f"不支持的Reranker提供商: {provider}")