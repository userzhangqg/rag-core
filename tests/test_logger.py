"""
Test cases for the logger module.
"""

import os
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.logger import setup_logger, get_logger
from conf.config import RAGConfig

def test_logger_setup():
    """Test that the logger can be set up correctly."""
    # Create a temporary config with a test log file
    with tempfile.TemporaryDirectory() as temp_dir:
        config = RAGConfig.from_config_file()
        config.logging_config.file = os.path.join(temp_dir, "test.log")
        
        # Setup logger
        logger = setup_logger(config)
        
        # Verify logger is set up
        assert logger is not None
        
        # Test logging
        logger.info("Test message")
        
        # Verify log file was created
        assert os.path.exists(config.logging_config.file)

def test_get_logger():
    """Test that we can get the logger instance."""
    # Setup logger first
    with tempfile.TemporaryDirectory() as temp_dir:
        config = RAGConfig.from_config_file()
        config.logging_config.file = os.path.join(temp_dir, "test.log")
        setup_logger(config)
        
        # Get logger
        logger = get_logger()
        
        # Verify we got a logger
        assert logger is not None