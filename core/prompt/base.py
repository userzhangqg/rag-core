#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prompt Engine Base Module for RAG Core System
"""


class PromptEngineBase:
    """Base class for prompt engine implementations."""
    
    def build_prompt(self, query: str, contexts: list, **kwargs) -> str:
        """
        Build a prompt for the LLM using the query and contexts.
        
        Args:
            query: The user's query
            contexts: List of context strings retrieved from the knowledge base
            **kwargs: Additional arguments
            
        Returns:
            Formatted prompt string
        """
        raise NotImplementedError