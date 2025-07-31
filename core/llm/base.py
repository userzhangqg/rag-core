#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM Base Module for RAG Core System
"""

class LLMBase:
    """Base class for LLM implementations."""
    
    def generate(self, prompt: str, **kwargs):
        """Generate text using the LLM."""
        raise NotImplementedError