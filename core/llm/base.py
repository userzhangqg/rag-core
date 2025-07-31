#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM Base Module for RAG Core System
"""

from utils.logger import get_module_logger
from conf.config import RAGConfig

class LLMBase:
    """Base class for LLM implementations."""
    
    def __init__(self):
        """
        Initialize the LLM base class.
        """
        self.logger = get_module_logger('llm')
        self.logger.debug("Initializing LLMBase")
    
    def generate(self, prompt: str, **kwargs):
        """Generate text using the LLM."""
        raise NotImplementedError