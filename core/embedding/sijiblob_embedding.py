#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow Embedding Module for RAG Core System
"""

import json
import requests
from typing import List, Union, Optional
from core.embedding.base import EmbeddingBase


class SiliconFlowEmbedding(EmbeddingBase):
    """SiliconFlow implementation of text embedding using their API."""
    
    def __init__(self, api_key: str, model_name: str = "BAAI/bge-large-zh-v1.5", api_url: str = "https://api.siliconflow.cn/v1/embeddings"):
        """
        Initialize the SiliconFlowEmbedding.
        
        Args:
            api_key: API key for SiliconFlow
            model_name: Name of the model to use for embedding
            api_url: URL of the SiliconFlow embedding API
        """
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_api_request(self, texts: List[str]) -> List[List[float]]:
        """
        Make API request to SiliconFlow.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings, one for each text
        """
        payload = {
            "model": self.model_name,
            "input": texts,
            "encoding_format": "float"
        }
        
        response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload))
        response.raise_for_status()
        
        result = response.json()
        return [item["embedding"] for item in result["data"]]
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings, one for each text
        """
        return self._make_api_request(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a query text.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding for the query text
        """
        return self._make_api_request([text])[0]
    
    def embed_text(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text(s).
        
        Args:
            text: Text or list of texts to embed
            
        Returns:
            Embedding(s) for the text(s)
        """
        if isinstance(text, str):
            return self.embed_query(text)
        else:
            return self.embed_documents(text)