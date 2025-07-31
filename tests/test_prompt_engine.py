#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for Prompt Engine
"""

import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.prompt.engine import PromptEngine


class TestPromptEngine(unittest.TestCase):
    def test_prompt_engine_initialization(self):
        """Test that the prompt engine can be initialized correctly."""
        prompt_engine = PromptEngine()
        self.assertIsInstance(prompt_engine, PromptEngine)
        
    def test_build_prompt_method_exists(self):
        """Test that the build_prompt method exists."""
        prompt_engine = PromptEngine()
        self.assertTrue(hasattr(prompt_engine, 'build_prompt'))
        
    def test_build_prompt_functionality(self):
        """Test that the build_prompt method works correctly."""
        prompt_engine = PromptEngine()
        query = "What is RAG?"
        contexts = ["RAG stands for Retrieval-Augmented Generation.", "It combines retrieval and generation."]
        prompt = prompt_engine.build_prompt(query, contexts)
        
        # Check that the prompt contains the query and contexts
        self.assertIn(query, prompt)
        for context in contexts:
            self.assertIn(context, prompt)


if __name__ == '__main__':
    unittest.main()