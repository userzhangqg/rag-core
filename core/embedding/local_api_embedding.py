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
from utils.logger import get_module_logger


class LocalAPIEmbedding(EmbeddingBase):
    """Local API implementation of text embedding using a local embedding service."""
    
    def __init__(self, api_url: str = "http://172.16.89.10:10669/scbllm/embedding-infer/embedding"):
        """
        Initialize the LocalAPIEmbedding.
        
        Args:
            api_url: URL of the local embedding API
        """
        super().__init__()
        self.api_url = api_url
        self.headers = {
            "Content-Type": "application/json"
        }
        # self.logger = get_module_logger('embedding.local_api')
        self.logger.info(f"LocalAPIEmbedding initialized with API URL: {api_url}")
    
    def _make_api_request(self, text: str) -> List[float]:
        """
        Make API request to local embedding service.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding for the text
        """
        self.logger.debug(f"Making API request for text: {text[:50]}...")
        
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
        
        try:
            response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload))
            response.raise_for_status()
            
            # Parse the response
            try:
                result = json.loads(response.json())
            except:
                result = json.loads(response.content)
            
            # Extract embeddings
            embeddings_list = result["embeddings_list"]
            self.logger.debug(f"Successfully generated embedding with {len(embeddings_list[0])} dimensions")
            return embeddings_list[0]  # Return the first (and only) embedding
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise
        except (KeyError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to parse API response: {str(e)}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings, one for each text
        """
        self.logger.info(f"Generating embeddings for {len(texts)} documents")
        embeddings = []
        for i, text in enumerate(texts):
            self.logger.debug(f"Processing document {i+1}/{len(texts)}")
            embedding = self._make_api_request(text)
            embeddings.append(embedding)
        self.logger.info(f"Successfully generated {len(embeddings)} embeddings")
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
        Generate embedding(s) for text(s).
        
        Args:
            text: Single text or list of texts to embed
            
        Returns:
            Single embedding or list of embeddings
        """
        if isinstance(text, str):
            self.logger.debug("Processing single text for embedding")
            return self.embed_query(text)
        else:
            self.logger.debug(f"Processing list of {len(text)} texts for embedding")
            return self.embed_documents(text)
