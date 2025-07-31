#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vector Base Module for RAG Core System
"""

from utils.logger import get_module_logger
from conf.config import RAGConfig

class VectorBase:
    """Base class for vector database implementations."""
    
    def __init__(self):
        """
        Initialize the vector base class.
        """
        self.logger = get_module_logger('vector')
        self.logger.debug("Initializing VectorBase")
    
    def embed(self, text: str, **kwargs):
        """Generate embeddings for the text."""
        raise NotImplementedError
        
    def search(self, query_vector, **kwargs):
        """Search for similar vectors."""
        raise NotImplementedError