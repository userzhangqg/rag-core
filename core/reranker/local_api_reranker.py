#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Local API Reranker Module for RAG Core System
"""

import json
import requests
import uuid
from typing import List
from core.reranker.base import RerankerBase


class LocalAPIReranker(RerankerBase):
    """Local API implementation of text reranking using a local reranking service."""
    
    def __init__(self, api_url: str = "http://172.16.89.10:10669/scbllm/embedding-infer/reranker"):
        """
        Initialize the LocalAPIReranker.
        
        Args:
            api_url: URL of the local reranking API
        """
        super().__init__()
        self.api_url = api_url
        self.headers = {
            "Content-Type": "application/json"
        }
        self.logger.info(f"LocalAPIReranker initialized with API URL: {api_url}")
    
    def _make_api_request(self, query: str, documents: List[str]) -> List[str]:
        """
        Make API request to local reranking service.
        
        Args:
            query: Query text
            documents: List of documents to rerank
            
        Returns:
            Reranked documents
        """
        self.logger.debug(f"Making reranking API request: query='{query[:50]}...', documents={len(documents)}")
        
        # Generate unique identifiers
        unique_uuid = str(uuid.uuid4())
        trace_id = f"trace-{unique_uuid}"
        
        payload = {
            "role": "assistant",
            "uuid": unique_uuid,
            "trace_id": trace_id,
            "query": query,
            "chunk_list": documents
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload))
            response.raise_for_status()
            
            # Parse the response
            try:
                result = json.loads(response.json())
            except:
                result = json.loads(response.content)
            
            # Extract reranked documents
            reranked_documents = result["rerank_datas"]
            self.logger.debug(f"Successfully reranked {len(reranked_documents)} documents")
            return reranked_documents
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Reranking API request failed: {str(e)}")
            raise
        except (KeyError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to parse reranking API response: {str(e)}")
            raise
    
    def rerank(self, query: str, documents: List[str], **kwargs) -> List[str]:
        """
        Rerank documents based on the query.
        
        Args:
            query: Query text
            documents: List of documents to rerank
            
        Returns:
            Reranked documents
        """
        self.logger.debug(f"Starting reranking process: query='{query[:50]}...', documents={len(documents)}")
        
        reranked_documents = self._make_api_request(query, documents)
        
        self.logger.info(f"Reranking completed: {len(reranked_documents)} documents reranked")
        return reranked_documents