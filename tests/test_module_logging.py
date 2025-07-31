#!/usr/bin/env python3
"""
测试模块级别日志控制功能
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger import setup_logger, get_module_logger
from conf.config import RAGConfig

def test_module_logging():
    """测试模块级别日志控制"""
    
    # 使用配置文件中的模块级别设置
    config = RAGConfig.from_config_file()
    
    print("=== 模块级别日志控制测试 ===")
    print(f"当前模块日志级别配置: {config.logging_config.module_levels}")
    
    # 初始化日志系统
    setup_logger(config)
    
    # 测试不同模块的日志输出
    modules = [
        "RAGPipeline",
        "DocumentProcessingPipeline", 
        "PromptEngine",
        "Retrieval",
        "Vector",
        "LLM",
        "UnknownModule"  # 应该使用默认级别
    ]
    
    for module_name in modules:
        logger = get_module_logger(module_name)
        
        print(f"\n--- 测试模块: {module_name} ---")
        print(f"配置级别: {config.logging_config.module_levels.get(module_name, 'default')}")
        
        # 测试不同级别的日志
        logger.debug(f"这是来自 {module_name} 的 DEBUG 日志")
        logger.info(f"这是来自 {module_name} 的 INFO 日志")
        logger.warning(f"这是来自 {module_name} 的 WARNING 日志")
        logger.error(f"这是来自 {module_name} 的 ERROR 日志")

if __name__ == "__main__":
    test_module_logging()