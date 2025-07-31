#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Retrieval Base Module for RAG Core System
"""

from utils.logger import get_module_logger
from conf.config import RAGConfig

class RetrievalBase:
    """Base class for retrieval implementations."""
    
    def __init__(self):
        """
        Initialize the retrieval base class.
        """
        self.logger = get_module_logger('retrieval')
        self.logger.debug("Initializing RetrievalBase")
    
    def search(self, query: str, **kwargs):
        """Search for documents based on the query."""
        raise NotImplementedError