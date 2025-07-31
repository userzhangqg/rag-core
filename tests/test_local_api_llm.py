#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for Local API LLM
"""

import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.llm.local_api_llm import LocalAPILLM


class TestLocalAPILLM(unittest.TestCase):
    def test_llm_initialization(self):
        """Test that the LLM can be initialized correctly."""
        llm = LocalAPILLM()
        self.assertIsInstance(llm, LocalAPILLM)
        
    def test_generate_method_exists(self):
        """Test that the generate method exists."""
        llm = LocalAPILLM()
        self.assertTrue(hasattr(llm, 'generate'))


if __name__ == '__main__':
    unittest.main()