#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM Factory Module for RAG Core System
"""

from typing import Optional
from core.llm.base import LLMBase
from core.llm.local_api_llm import LocalAPILLM


class LLMFactory:
    """Factory class for creating LLM instances based on configuration."""
    
    @staticmethod
    def create_llm(provider: str = "local_api", 
                   api_key: Optional[str] = None, 
                   model_name: Optional[str] = None,
                   api_url: Optional[str] = None) -> LLMBase:
        """
        Create an LLM instance based on the provider.
        
        Args:
            provider: LLM provider name (e.g., "local_api", "openai")
            api_key: API key for the LLM service
            model_name: Model name to use
            api_url: API URL for the LLM service
            
        Returns:
            LLMBase: LLM instance
        
        Raises:
            ValueError: If the provider is not supported
        """
        if provider == "local_api":
            return LocalAPILLM(api_url=api_url or "http://172.16.89.10:10669/scbllm/llm-infer/chat")
        # elif provider == "openai":
        #     # 这里可以添加OpenAI的实现
        #     # return OpenAILLM(api_key=api_key, model_name=model_name)
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")