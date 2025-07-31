#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Retrieval Base Module for RAG Core System
"""

class RetrievalBase:
    """Base class for retrieval implementations."""
    
    def search(self, query: str, **kwargs):
        """Search for documents based on the query."""
        raise NotImplementedError