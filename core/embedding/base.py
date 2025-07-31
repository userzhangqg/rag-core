#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Embedding Base Module for RAG Core System
"""

from abc import ABC, abstractmethod
from typing import List, Union
from utils.logger import get_module_logger
from conf.config import RAGConfig


class EmbeddingBase(ABC):
    """Base class for text embedding implementations."""
    
    def __init__(self):
        """
        Initialize the embedding base class.
        """
        self.logger = get_module_logger('embedding')
        self.logger.debug("Initializing EmbeddingBase")
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings, one for each text
        """
        pass
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a query text.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding for the query text
        """
        pass
    
    @abstractmethod
    def embed_text(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text(s).
        
        Args:
            text: Text or list of texts to embed
            
        Returns:
            Embedding(s) for the text(s)
        """
        pass