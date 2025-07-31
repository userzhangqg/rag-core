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
        super().__init__()
        self.system_prompt = system_prompt
        self.logger.info(f"Initialized with system prompt: {system_prompt[:50]}...")
    
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
        self.logger.debug(f"Building prompt for query: '{query[:50]}...'")
        self.logger.debug(f"Number of contexts: {len(contexts)}")
        
        # Get system prompt from kwargs or use default
        system_prompt = kwargs.get('system_prompt', self.system_prompt)
        self.logger.debug(f"Using system prompt: {system_prompt[:50]}...")
        
        # Build context string
        context_str = "\n".join([f"{i+1}. {context}" for i, context in enumerate(contexts)])
        self.logger.debug(f"Generated context string with {len(contexts)} items")
        
        # Format the prompt
        prompt = f"""{system_prompt}

Context information:
{context_str}

Question: {query}

Please provide a concise and accurate answer based on the context information above."""
        
        prompt_length = len(prompt)
        self.logger.debug(f"Generated prompt with {prompt_length} characters")
        
        return prompt