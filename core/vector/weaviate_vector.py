#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Weaviate Vector Store Module for RAG Core System
"""

from typing import List, Dict, Any, Optional, Union
from core.embedding.base import EmbeddingBase
from conf.config import Config
import weaviate
import weaviate.exceptions
import logging

class WeaviateVector:
    """Weaviate implementation of vector database operations."""
    
    def __init__(self, 
            embedding_model: Optional[EmbeddingBase] = None,
            weaviate_url: str = "http://localhost:8080",
            grpc_port: int = 50051,
            index_name: str = "RAGIndex",
        ):
        """
        Initialize the WeaviateVector.
        
        Args:
            embedding_model: EmbeddingBase instance to use for generating embeddings
            weaviate_url: URL of the Weaviate instance
            grpc_port: gRPC port for Weaviate connection
            index_name: Name of the index in Weaviate
        """
        self.weaviate_url = weaviate_url
        self.index_name = index_name
        
        # Initialize embedding model if not provided
        if embedding_model is None:
            raise ValueError("embedding_model参数不能为空，请提供一个EmbeddingBase实例")
        self.embedding_model = embedding_model
        
        # Initialize Weaviate client

        connection_params = weaviate.connect.ConnectionParams.from_url(
            url=weaviate_url,
            grpc_port=grpc_port
        )
        client = weaviate.WeaviateClient(connection_params=connection_params, skip_init_checks=True)
        client.connect()

        self.client = client
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize index
        self.index = True
    
    def close(self):
            """Close the Weaviate client connection."""
            if hasattr(self, 'client'):
                self.client.close()

    @classmethod
    def from_config(cls, embedding_model: Optional[EmbeddingBase] = None, **kwargs):
        """
        Create WeaviateVector instance from configuration.
        
        Args:
            embedding_model: EmbeddingBase instance to use for generating embeddings
            **kwargs: Additional keyword arguments to override config
            
        Returns:
            WeaviateVector instance configured from config file
        """
        weaviate_url = kwargs.pop('weaviate_url', Config.VECTOR_DB_URL)
        grpc_port = kwargs.pop('grpc_port', Config.VECTOR_DB_GRPC_PORT)
        
        return cls(
            embedding_model=embedding_model,
            weaviate_url=weaviate_url,
            grpc_port=grpc_port,
            **kwargs
        )
        
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding for the text
        """
        return self.embedding_model.embed_text(text)
    
    def store_texts(self, texts: List[str], metadata: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Store texts and their embeddings in the vector database.
        
        Args:
            texts: List of texts to store
            metadata: Optional list of metadata dictionaries for each text
            
        Returns:
            List of node IDs for the stored texts
        """
        # Create schema if it doesn't exist
        schema = {
            "class": self.index_name,
            "properties": [
                {
                    "name": "text",
                    "dataType": ["text"],
                }
            ],
        }
        
        if not self.client.collections.exists(self.index_name):
            self.client.collections.create_from_dict(schema)
        
        # Get collection
        collection = self.client.collections.get(self.index_name)
        
        # Generate embeddings for texts
        embeddings = [self.embed(text) for text in texts]
        
        # Store texts and embeddings
        ids = []
        try:
            with collection.batch.dynamic() as batch:
                for i, text in enumerate(texts):
                    data_properties = {"text": text}
                    if metadata is not None and i < len(metadata):
                        # metadata maybe None
                        for key, val in (metadata[i] or {}).items():
                            data_properties[key] = val
                    
                    
                    uuid = str(batch.add_object(
                        properties=data_properties,
                        vector=embeddings[i] if embeddings else None,
                    ))
                    ids.append(uuid)
                    
                    # 检查批处理错误
                    if hasattr(batch, 'number_errors') and batch.number_errors > 10:
                        self.logger.warning("Batch import stopped due to excessive errors.")
                        break
                        
                self.logger.info(f"Successfully queued {len(texts)} objects to Weaviate batch")
        except weaviate.exceptions.WeaviateConnectionError as e:
            self.logger.error(f"Weaviate Connection Error: {e}")
            raise RuntimeError("Failed to connect to Weaviate service. Please check if the service is running.") from e
        except Exception as e:
            self.logger.error(f"Unknown error occurred during batch processing: {e}")
            raise
        
        failed = collection.batch.failed_objects
        if failed:
            raise weaviate.exceptions.WeaviateBatchError(f"Failed inserts: {failed}")
        
        # self.index = True  # Indicate index exists
        return ids
    
    def search(self, query: str, top_k: int = 5, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for similar texts in the vector database.
        
        Args:
            query: Query text
            top_k: Number of results to return
            score_threshold: Minimum similarity score for results
            
        Returns:
            List of search results with text, metadata, and similarity score
        """
        if self.index is None:
            raise ValueError("Index not initialized. Store some texts first.")
        
        # Generate embedding for query
        query_vector = self.embed(query)
        
        # Perform search
        return self.search_by_vector(query_vector, top_k, score_threshold)
    
    def search_by_vector(self, query_vector: List[float], top_k: int = 5, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for similar texts using a query vector.
        
        Args:
            query_vector: Query vector
            top_k: Number of results to return
            score_threshold: Minimum similarity score for results
            
        Returns:
            List of search results with text, metadata, and similarity score
        """
        if self.index is None:
            raise ValueError("Index not initialized. Store some texts first.")
        
        # Get collection
        collection = self.client.collections.get(self.index_name)
        
        # Perform vector search
        result = collection.query.near_vector(
            near_vector=query_vector,
            limit=top_k,
            return_properties=["text"],
            return_metadata=["distance"]
        )
        
        # Process results
        docs = []
        for obj in result.objects:
            text = obj.properties.get("text", "")
            distance = obj.metadata.distance if obj.metadata else 0.0
            score = 1 - distance  # Convert distance to similarity score
            
            # Check score threshold
            if score > score_threshold:
                docs.append({
                    "text": text,
                    "metadata": obj.properties,
                    "score": score
                })
        
        # Sort by score in descending order
        docs = sorted(docs, key=lambda x: x["score"], reverse=True)
        return docs