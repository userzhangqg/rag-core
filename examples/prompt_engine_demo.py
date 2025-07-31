#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example usage of Prompt Engine for RAG Core System
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.prompt.engine import PromptEngine


def main():
    # Initialize the PromptEngine
    prompt_engine = PromptEngine()
    
    # Define query and contexts
    query = "什么是RAG?"
    contexts = [
        "RAG代表Retrieval-Augmented Generation，是一种结合了信息检索和文本生成的技术。",
        "在RAG系统中，首先从知识库中检索相关信息，然后利用这些信息生成回答。",
        "RAG技术可以提高大型语言模型的准确性和相关性。"
    ]
    
    # Build prompt
    prompt = prompt_engine.build_prompt(query, contexts)
    print("Generated Prompt:")
    print(prompt)
    
    # Build prompt with custom system prompt
    custom_system_prompt = "你是一个专业的AI助手，请根据提供的上下文信息回答问题。"
    custom_prompt = prompt_engine.build_prompt(query, contexts, system_prompt=custom_system_prompt)
    print("\nGenerated Prompt with Custom System Prompt:")
    print(custom_prompt)


if __name__ == "__main__":
    main()