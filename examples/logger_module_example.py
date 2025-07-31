"""
Example usage of the logger module.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.logger import setup_logger, get_logger, get_module_logger
from conf.config import RAGConfig

def main():
    # Load configuration
    config = RAGConfig.from_config_file()
    
    # Setup logger with configuration
    logger = setup_logger(config)
    
    # Get logger instance
    log = get_module_logger("parser")
    
    # Test logging at different levels
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    
    print("Logger example completed. Check the logs directory for output.")


if __name__ == "__main__":
    main()