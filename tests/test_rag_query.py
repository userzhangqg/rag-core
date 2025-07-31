#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for the RAG Pipeline query functionality in RAG Core System
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.pipeline.rag_pipeline import RAGPipeline, RAGConfig


class TestRAGPipelineQuery(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.pipeline = RAGPipeline()
    
    def test_query_method_exists(self):
        """Test that the query method exists and is callable"""
        self.assertTrue(hasattr(self.pipeline, 'query'))
        self.assertTrue(callable(getattr(self.pipeline, 'query', None)))
    
    @patch('core.pipeline.rag_pipeline.VectorRetriever')
    @patch('core.llm.factory.LLMFactory.create_llm')
    def test_query_with_mock_components(self, mock_create_llm, mock_retriever):
        """Test query method with mocked components"""
        # Mock the retriever response
        mock_retriever_instance = Mock()
        mock_retriever_instance.search.return_value = [
            {'text': 'This is a retrieved document.', 'metadata': {}, 'score': 0.9}
        ]
        mock_retriever.return_value = mock_retriever_instance
        
        # Mock the LLM response
        mock_llm_instance = Mock()
        mock_llm_instance.generate.return_value = "This is a generated response."
        mock_create_llm.return_value = mock_llm_instance
        
        # Create a new pipeline with mocked components
        # Note: The pipeline must be created after the mocks are set up
        pipeline = RAGPipeline()
        
        # Test the query method
        query_text = "What is RAG?"
        response = pipeline.query(query_text)
        
        # Verify the response
        self.assertEqual(response, "This is a generated response.")
        
        # Verify that the retriever was called with the correct query and parameters
        mock_retriever_instance.search.assert_called_once_with(query_text, 5, 0.0)
        
        # Verify that the LLM was called with a prompt
        mock_llm_instance.generate.assert_called_once()


def main():
    unittest.main()


if __name__ == "__main__":
    main()