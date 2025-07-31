#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global logging utility for RAG Core system.
Provides centralized logging configuration with support for both console and file output.
"""

import os
import sys
import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict, Any
import yaml


class RAGLogger:
    """RAG Core system logger with configurable output and debug mode support."""
    
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.config = None
        self.debug_mode = False
        self._setup_config()
    
    def _setup_config(self):
        """Load logging configuration from config file."""
        config_path = os.environ.get('RAG_CORE_CONFIG', 'conf/config.yaml')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f) or {}
                    self.config = config.get('logging', {})
                    self.debug_mode = config.get('debug', {}).get('enabled', False)
            except Exception as e:
                print(f"Warning: Failed to load logging config: {e}")
                self.config = {}
        else:
            self.config = {}
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a configured logger instance for the specified module."""
        if name in self._loggers:
            return self._loggers[name]
        
        logger = logging.getLogger(name)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Set level based on debug mode
        if self.debug_mode:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(getattr(logging, self.config.get('level', 'INFO').upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            fmt=self.config.get('format', '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'),
            datefmt=self.config.get('date_format', '%Y-%m-%d %H:%M:%S')
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, self.config.get('console_level', 'INFO').upper()))
        logger.addHandler(console_handler)
        
        # File handler
        log_file = self.config.get('file', 'logs/rag_core.log')
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.config.get('max_file_size', 10 * 1024 * 1024),  # 10MB
            backupCount=self.config.get('backup_count', 5)
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, self.config.get('file_level', 'DEBUG').upper()))
        logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        self._loggers[name] = logger
        return logger
    
    def set_debug_mode(self, enabled: bool):
        """Enable or disable debug mode globally."""
        self.debug_mode = enabled
        for logger in self._loggers.values():
            if enabled:
                logger.setLevel(logging.DEBUG)
            else:
                logger.setLevel(getattr(logging, self.config.get('level', 'INFO').upper()))
    
    def get_config(self) -> Dict[str, Any]:
        """Get current logging configuration."""
        return {
            'debug_mode': self.debug_mode,
            'config': self.config
        }


# Global logger instance
_rag_logger = RAGLogger()


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger for the specified module name."""
    return _rag_logger.get_logger(name)


def set_debug_mode(enabled: bool):
    """Set global debug mode for all loggers."""
    _rag_logger.set_debug_mode(enabled)


def get_logging_config() -> Dict[str, Any]:
    """Get current logging configuration."""
    return _rag_logger.get_config()


# Convenience functions for common logging patterns
class ModuleLogger:
    """Context-aware logger for RAG modules with debug helpers."""
    
    def __init__(self, module_name: str):
        self.logger = get_logger(module_name)
        self.module_name = module_name
    
    def debug_process(self, process_name: str, **kwargs):
        """Log debug information about a process."""
        if _rag_logger.debug_mode:
            self.logger.debug(f"[{process_name}] {kwargs}")
    
    def info_process(self, process_name: str, message: str, **kwargs):
        """Log info about a process."""
        if kwargs:
            self.logger.info(f"[{process_name}] {message} - {kwargs}")
        else:
            self.logger.info(f"[{process_name}] {message}")
    
    def warn_process(self, process_name: str, message: str, **kwargs):
        """Log warning about a process."""
        if kwargs:
            self.logger.warning(f"[{process_name}] {message} - {kwargs}")
        else:
            self.logger.warning(f"[{process_name}] {message}")
    
    def error_process(self, process_name: str, message: str, **kwargs):
        """Log error about a process."""
        if kwargs:
            self.logger.error(f"[{process_name}] {message} - {kwargs}")
        else:
            self.logger.error(f"[{process_name}] {message}")
    
    def log_document_info(self, doc_info: Dict[str, Any]):
        """Log document parsing information."""
        if _rag_logger.debug_mode:
            self.logger.debug(f"[Document] Parsed document info: {doc_info}")
    
    def log_chunking_info(self, chunk_count: int, chunk_size: int, total_chars: int):
        """Log chunking process information."""
        if _rag_logger.debug_mode:
            self.logger.debug(
                f"[Chunking] Created {chunk_count} chunks "
                f"(size: {chunk_size}, total: {total_chars} chars)"
            )
    
    def log_embedding_info(self, embedded_count: int, model_name: str, dimensions: int):
        """Log embedding process information."""
        if _rag_logger.debug_mode:
            self.logger.debug(
                f"[Embedding] Embedded {embedded_count} documents "
                f"(model: {model_name}, dimensions: {dimensions})"
            )
    
    def log_retrieval_info(self, query: str, retrieved_count: int, top_k: int, scores: list = None):
        """Log retrieval process information."""
        if _rag_logger.debug_mode:
            info = f"[Retrieval] Query: '{query}' -> Retrieved {retrieved_count}/{top_k} documents"
            if scores:
                info += f" (scores: {scores})"
            self.logger.debug(info)
    
    def log_rerank_info(self, original_count: int, reranked_count: int, top_n: int):
        """Log reranking process information."""
        if _rag_logger.debug_mode:
            self.logger.debug(
                f"[Rerank] Reranked {original_count} documents -> "
                f"Selected top {reranked_count}/{top_n}"
            )
    
    def log_llm_info(self, prompt_type: str, input_length: int, output_length: int, model_name: str):
        """Log LLM process information."""
        if _rag_logger.debug_mode:
            self.logger.debug(
                f"[LLM] {prompt_type} - Input: {input_length} chars, "
                f"Output: {output_length} chars (model: {model_name})"
            )


def create_module_logger(module_name: str) -> ModuleLogger:
    """Create a module-specific logger with debug helpers."""
    return ModuleLogger(module_name)