#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reranker Base Module for RAG Core System
"""

class RerankerBase:
    """Base class for reranker implementations."""
    
    def rerank(self, query: str, documents: list, **kwargs):
        """Rerank documents based on the query."""
        raise NotImplementedError