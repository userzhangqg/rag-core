#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Local API Embedding Module for RAG Core System
"""

import json
import requests
import uuid
from typing import List, Union, Optional
from core.embedding.base import EmbeddingBase


class LocalAPIEmbedding(EmbeddingBase):
    """Local API implementation of text embedding using a local embedding service."""
    
    def __init__(self, api_url: str = "http://172.16.89.10:10669/scbllm/embedding-infer/embedding"):
        """
        Initialize the LocalAPIEmbedding.
        
        Args:
            api_url: URL of the local embedding API
        """
        self.api_url = api_url
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def _make_api_request(self, text: str) -> List[float]:
        """
        Make API request to local embedding service.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding for the text
        """
        # Generate unique identifiers
        unique_uuid = str(uuid.uuid4())
        trace_id = f"trace-{unique_uuid}"
        
        payload = {
            "role": "user",
            "uuid": unique_uuid,
            "trace_id": trace_id,
            "embedding_text": text,
            "query": False
        }
        
        response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload))
        response.raise_for_status()
        
        # Parse the response
        try:
            result = json.loads(response.json())
        except:
            result = json.loads(response.content)
        
        # Extract embeddings
        embeddings_list = result["embeddings_list"]
        return embeddings_list[0]  # Return the first (and only) embedding
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings, one for each text
        """
        embeddings = []
        for text in texts:
            embedding = self._make_api_request(text)
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a query text.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding for the query text
        """
        return self._make_api_request(text)
    
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
