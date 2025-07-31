#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for Local API Reranker
"""

import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.reranker.local_api_reranker import LocalAPIReranker


class TestLocalAPIReranker(unittest.TestCase):
    def test_reranker_initialization(self):
        """Test that the reranker can be initialized correctly."""
        reranker = LocalAPIReranker()
        self.assertIsInstance(reranker, LocalAPIReranker)
        
    def test_rerank_method_exists(self):
        """Test that the rerank method exists."""
        reranker = LocalAPIReranker()
        self.assertTrue(hasattr(reranker, 'rerank'))


if __name__ == '__main__':
    unittest.main()