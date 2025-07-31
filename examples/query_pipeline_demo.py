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
    rag_config = RAGConfig().from_config_file()
    rag_pipeline = RAGPipeline(rag_config)
    
    # Query the pipeline
    query = "介绍一下Refly项目"
    response = rag_pipeline.query(query)
    print(f"\nQuery: {query}")
    print(f"Response: {response}")


if __name__ == "__main__":
    main()