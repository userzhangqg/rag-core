#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example usage of RAG Pipeline for RAG Core System
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.pipeline.rag_pipeline import RAGPipeline, RAGConfig


def main():
    # Create a RAG pipeline with default configuration
    rag_pipeline = RAGPipeline()
    
    # Process a text content
    content = """
    Retrieval-Augmented Generation (RAG) is a technique that combines information retrieval 
    and text generation to improve the quality of language model outputs. 
    
    In a RAG system, when a query is received, the system first retrieves relevant documents 
    from a knowledge base using a retrieval mechanism. Then, it uses these documents as 
    context to generate a more informed and accurate response.
    
    The key benefits of RAG include:
    1. Improved accuracy by grounding responses in real-world knowledge
    2. Reduced hallucination by relying on retrieved facts
    3. Enhanced relevance by using contextually appropriate information
    4. Better handling of domain-specific queries
    """
    
    chunks = rag_pipeline.process_content(content, "RAG Introduction")
    print(f"Processed content into {len(chunks)} chunks")
    
    # Query the pipeline
    query = "What are the benefits of RAG?"
    response = rag_pipeline.query(query)
    print(f"\nQuery: {query}")
    print(f"Response: {response}")


if __name__ == "__main__":
    main()