#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example usage of Local API LLM for RAG Core System
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.llm.local_api_llm import LocalAPILLM


def main():
    # Initialize the LocalAPILLM
    llm = LocalAPILLM()
    
    # Define query
    query = "什么是rag"
    
    # Generate text (non-streaming)
    print("Non-streaming response:")
    response = llm.generate(query, streaming=False)
    print(response)
    
    # Generate text (streaming)
    print("\nStreaming response:")
    response_stream = llm.generate(query, streaming=True)
    for chunk in response_stream:
        print(chunk, end='', flush=True)
    print()  # New line at the end


if __name__ == "__main__":
    main()