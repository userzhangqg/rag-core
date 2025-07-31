#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example usage of Local API Reranker for RAG Core System
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.reranker.local_api_reranker import LocalAPIReranker


def main():
    # Initialize the LocalAPIReranker
    reranker = LocalAPIReranker()
    
    # Define query and documents
    query = "aa"
    documents = ["aa", "bb", "cc", "dd", "aa", "bb", "cc", "dd"]
    
    # Rerank documents
    reranked_documents = reranker.rerank(query, documents)
    
    # Print results
    print("Query:", query)
    print("Original documents:", documents)
    print("Reranked documents:", reranked_documents)


if __name__ == "__main__":
    main()