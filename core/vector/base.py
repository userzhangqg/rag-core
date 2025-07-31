#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vector Base Module for RAG Core System
"""

class VectorBase:
    """Base class for vector database implementations."""
    
    def embed(self, text: str, **kwargs):
        """Generate embeddings for the text."""
        raise NotImplementedError
        
    def search(self, query_vector, **kwargs):
        """Search for similar vectors."""
        raise NotImplementedError