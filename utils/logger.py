"""
Logger module using Loguru for global logging configuration.
This module provides a configured logger that can output to both console and file.
"""

import os
from loguru import logger
from conf.config import RAGConfig


class ModuleLogger:
    """Module-specific logger wrapper for better logging organization."""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.logger = logger.bind(module=module_name)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with module context."""
        self.logger.debug(f"[{self.module_name}] {message}", **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with module context."""
        self.logger.info(f"[{self.module_name}] {message}", **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with module context."""
        self.logger.warning(f"[{self.module_name}] {message}", **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with module context."""
        self.logger.error(f"[{self.module_name}] {message}", **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with module context."""
        self.logger.critical(f"[{self.module_name}] {message}", **kwargs)


def setup_logger(config: RAGConfig = None):
    """
    Setup the global logger with configuration from the config file.
    
    Args:
        config (RAGConfig, optional): Configuration object. If None, will use default config.
    """
    if config is None:
        config = RAGConfig.from_config_file()
    
    # Remove default logger
    logger.remove()
    
    # 创建模块过滤器函数
    def module_filter(record):
        """根据模块名称过滤日志级别"""
        module_name = record["extra"].get("module", "default")
        module_level = config.logging_config.module_levels.get(
            module_name, 
            config.logging_config.module_levels.get("default", "DEBUG")
        )
        
        # 将字符串级别转换为数值
        level_mapping = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50
        }
        
        module_level_num = level_mapping.get(module_level.upper(), 20)
        # print(f"record level: {record['level'].no}, module_level_num: {module_level_num}")
        return record["level"].no >= module_level_num
    
    # Add console logger
    logger.add(
        lambda msg: print(msg, end=''),
        level=config.logging_config.console_level,
        format=config.logging_config.format,
        filter=module_filter,
        colorize=True,
        serialize=False
    )
    
    # Add file logger
    log_file = config.logging_config.file
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True) if os.path.dirname(log_file) else None
    
    logger.add(
        log_file,
        level=config.logging_config.file_level,
        format=config.logging_config.format,
        rotation=config.logging_config.max_file_size,
        retention=config.logging_config.backup_count,
        encoding="utf-8",
        serialize=False,
        filter=module_filter
    )
    
    return logger


def get_logger():
    """
    Get the configured logger instance.
    
    Returns:
        logger: The configured logger instance.
    """
    return logger


def get_module_logger(module_name: str) -> ModuleLogger:
    """
    Get a module-specific logger instance.
    
    Args:
        module_name (str): Name of the module for logging context.
        
    Returns:
        ModuleLogger: Module-specific logger instance.
    """
    return ModuleLogger(module_name)
