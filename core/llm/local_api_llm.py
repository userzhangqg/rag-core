#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Local API LLM Module for RAG Core System
"""

import json
import requests
import uuid
from typing import Union, Iterator
from core.llm.base import LLMBase


class LocalAPILLM(LLMBase):
    """Local API implementation of LLM inference using a local LLM service."""
    
    def __init__(self, api_url: str = "http://172.16.89.10:9648/scbllm/llm-2025/llm_infer"):
        """
        Initialize the LocalAPILLM.
        
        Args:
            api_url: URL of the local LLM API
        """
        super().__init__()
        self.api_url = api_url
        self.headers = {
            "Content-Type": "application/json"
        }
        self.logger.info(f"LocalAPILLM initialized with API URL: {api_url}")
    
    def _make_api_request(self, query: str, system_prompt: str = "You are a helpful assistant.", 
                         top_k: int = 1, max_output_length: int = 8192, 
                         repetition_penalty: int = 1, enable_thinking: bool = False, 
                         streaming: bool = False) -> Union[str, Iterator[str]]:
        """
        Make API request to local LLM service.
        
        Args:
            query: Query text
            system_prompt: System prompt for the LLM
            top_k: Top K value for sampling
            max_output_length: Maximum output length
            repetition_penalty: Repetition penalty
            enable_thinking: Enable thinking mode
            streaming: Enable streaming mode
            
        Returns:
            Generated text or iterator of text chunks
        """
        self.logger.debug(f"Making LLM API request: query='{query[:50]}...', streaming={streaming}")
        
        # Generate unique identifier
        trace_id = str(uuid.uuid4())
        
        payload = {
            "query": query,
            "system_prompt": system_prompt,
            "top_k": top_k,
            "max_output_length": max_output_length,
            "repetition_penalty": repetition_penalty,
            "enable_thinking": enable_thinking,
            "streaming": streaming
        }
        
        try:
            if streaming:
                # For streaming, we need to handle the response differently
                response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload), stream=True)
                response.raise_for_status()
                
                self.logger.debug("LLM streaming response initiated")
                
                # Return an iterator of text chunks
                def text_chunk_iterator():
                    chunk_count = 0
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            try:
                                result = json.loads(decoded_line)
                                chunk = result["answer"]
                                chunk_count += 1
                                self.logger.debug(f"Received streaming chunk {chunk_count}: {len(chunk)} chars")
                                yield chunk
                            except json.JSONDecodeError:
                                # If we can't parse the line as JSON, skip it
                                continue
                    self.logger.debug(f"Streaming completed: {chunk_count} chunks received")
                
                return text_chunk_iterator()
            else:
                # For non-streaming, return the complete response
                response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload))
                response.raise_for_status()
                
                # Parse the response
                try:
                    result = json.loads(response.json())
                except:
                    result = json.loads(response.content)
                
                # Extract the answer
                answer = result["answer"][0] if isinstance(result["answer"], list) else result["answer"]
                self.logger.debug(f"LLM response received: {len(str(answer))} characters")
                return answer
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"LLM API request failed: {str(e)}")
            raise
        except (KeyError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to parse LLM API response: {str(e)}")
            raise
    
    def generate(self, prompt: str, **kwargs) -> Union[str, Iterator[str]]:
        """
        Generate text using the LLM.
        
        Args:
            prompt: Prompt for the LLM
            **kwargs: Additional arguments (system_prompt, top_k, max_output_length, 
                     repetition_penalty, enable_thinking, streaming)
            
        Returns:
            Generated text or iterator of text chunks
        """
        streaming = kwargs.get('streaming', False)
        self.logger.debug(f"Starting text generation: prompt='{prompt[:50]}...', streaming={streaming}")
        # self.logger.debug(prompt)
        
        result = self._make_api_request(prompt, **kwargs)
        
        if streaming:
            self.logger.debug("Returning streaming iterator")
        else:
            self.logger.debug(f"Text generation completed: {len(str(result))} characters generated")
        
        return result