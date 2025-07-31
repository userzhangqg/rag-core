#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prompt Engine Implementation for RAG Core System
"""

from core.prompt.base import PromptEngineBase


class PromptEngine(PromptEngineBase):
    """Implementation of prompt engine for RAG systems."""
    
    def __init__(self, system_prompt: str = "You are a helpful assistant."):
        """
        Initialize the PromptEngine.
        
        Args:
            system_prompt: Default system prompt
        """
        self.system_prompt = system_prompt
    
    def build_prompt(self, query: str, contexts: list, **kwargs) -> str:
        """
        Build a prompt for the LLM using the query and contexts.
        
        Args:
            query: The user's query
            contexts: List of context strings retrieved from the knowledge base
            **kwargs: Additional arguments (system_prompt)
            
        Returns:
            Formatted prompt string
        """
        # Get system prompt from kwargs or use default
        system_prompt = kwargs.get('system_prompt', self.system_prompt)
        
        # Build context string
        context_str = "\n".join([f"{i+1}. {context}" for i, context in enumerate(contexts)])
        
        # Format the prompt
        prompt = f"""{system_prompt}

Context information:
{context_str}

Question: {query}

Please provide a concise and accurate answer based on the context information above."""
        
        return prompt