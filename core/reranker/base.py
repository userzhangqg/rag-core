#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reranker Base Module for RAG Core System
"""

from utils.logger import get_module_logger
from conf.config import RAGConfig

class RerankerBase:
    """Base class for reranker implementations."""
    
    def __init__(self):
        """
        Initialize the reranker base class.
        """
        self.logger = get_module_logger('reranker')
        self.logger.debug("Initializing RerankerBase")
    
    def rerank(self, query: str, documents: list, **kwargs):
        """Rerank documents based on the query."""
        raise NotImplementedError