#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG Core System Configuration
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class LoggingConfig:
    """
    日志配置参数
    """
    level: str = "INFO"
    console_level: str = "INFO"
    file_level: str = "DEBUG"
    file: str = "logs/rag_core.log"
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    format: str = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"


@dataclass
class DebugConfig:
    """
    调试模式配置
    """
    enabled: bool = False


@dataclass
class RAGConfig:
    """
    RAG配置参数
    """
    # 分块参数
    chunk_size: int = 1000
    chunk_overlap: int = 200
    separators: Optional[List[str]] = None
    
    # 解析参数
    parse_by_chapter: bool = False  # 是否按章节解析
    parse_by_element: bool = False   # 是否按元素解析
    remove_hyperlinks: bool = False
    remove_images: bool = False
    enable_metadata: bool = True
    
    # 向量化参数
    batch_size: int = 32
    embedding_provider: str = "local_api"
    embedding_api_key: Optional[str] = None
    embedding_model_name: Optional[str] = None
    embedding_api_url: Optional[str] = None
    
    # 向量数据库参数
    vector_db_url: Optional[str] = None
    
    # LLM参数
    llm_provider: str = "local_api"
    llm_api_key: Optional[str] = None
    llm_model_name: Optional[str] = None
    llm_api_url: Optional[str] = None
    
    # Rerank参数
    rerank_provider: str = "local_api"
    rerank_api_url: Optional[str] = None
    
    # 查询参数
    retrieve_top_k: int = 50
    rerank_top_n: int = 5
    
    # 日志配置
    logging_config: LoggingConfig = field(default_factory=LoggingConfig)
    debug_config: DebugConfig = field(default_factory=DebugConfig)
    
    # 其他参数
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_config_file(cls, config_file: str = None) -> 'RAGConfig':
        """
        从配置文件创建RAGConfig实例
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            RAGConfig: 配置实例
        """
        if config_file is None:
            config_file = os.environ.get('RAG_CORE_CONFIG', 'conf/config.yaml')
        
        # 加载配置文件
        _config = {}
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                _config = yaml.safe_load(f) or {}
        
        # 从配置文件中读取RAG相关配置
        rag_config = _config.get('rag', {})
        
        # 从配置文件中读取日志配置
        logging_config = _config.get('logging', {})
        debug_config = _config.get('debug', {})
        
        # 创建RAGConfig实例
        return cls(
            chunk_size=rag_config.get('chunk_size', 1000),
            chunk_overlap=rag_config.get('chunk_overlap', 200),
            separators=rag_config.get('separators', None),
            parse_by_chapter=rag_config.get('parse_by_chapter', True),
            parse_by_element=rag_config.get('parse_by_element', False),
            remove_hyperlinks=rag_config.get('remove_hyperlinks', False),
            remove_images=rag_config.get('remove_images', False),
            enable_metadata=rag_config.get('enable_metadata', True),
            batch_size=rag_config.get('batch_size', 32),
            embedding_provider=_config.get('embedding', {}).get('provider', "local_api"),
            embedding_api_key=_config.get('embedding', {}).get('siliconflow', {}).get('api_key'),
            embedding_model_name=_config.get('embedding', {}).get('siliconflow', {}).get('model_name'),
            embedding_api_url=_config.get('embedding', {}).get('local_api', {}).get('url') if _config.get('embedding', {}).get('provider') == "local_api" else _config.get('embedding', {}).get('siliconflow', {}).get('api_url'),
            vector_db_url=_config.get('vector_db', {}).get('url'),
            llm_provider=_config.get('llm', {}).get('provider', "local_api"),
            llm_api_key=_config.get('llm', {}).get('api_key'),
            llm_model_name=_config.get('llm', {}).get('model'),
            llm_api_url=_config.get('llm', {}).get('local_api', {}).get('url'),
            rerank_provider=_config.get('rerank', {}).get('provider', "local_api"),
            rerank_api_url=_config.get('rerank', {}).get('local_api', {}).get('url'),
            retrieve_top_k=rag_config.get('retrieve_top_k', 50),
            rerank_top_n=rag_config.get('rerank_top_n', 5),
            logging_config=LoggingConfig(
                level=logging_config.get('level', 'INFO'),
                console_level=logging_config.get('console_level', 'INFO'),
                file_level=logging_config.get('file_level', 'DEBUG'),
                file=logging_config.get('file', 'logs/rag_core.log'),
                max_file_size=logging_config.get('max_file_size', 10485760),
                backup_count=logging_config.get('backup_count', 5),
                format=logging_config.get('format', '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'),
                date_format=logging_config.get('date_format', '%Y-%m-%d %H:%M:%S')
            ),
            debug_config=DebugConfig(
                enabled=debug_config.get('enabled', False)
            )
        )
    
    def update(self, **kwargs) -> None:
        """
        更新配置参数
        
        Args:
            **kwargs: 配置参数
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Config:
    """Configuration class for the RAG Core system."""
    
    # Default configuration file path
    CONFIG_FILE = os.environ.get('RAG_CORE_CONFIG', 'conf/config.yaml')
    
    # Load configuration from YAML file
    _config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            _config = yaml.safe_load(f) or {}
    
    # Database configuration
    DATABASE_URL = _config.get('database', {}).get('url', "postgresql://user:password@localhost/rag_core")
    
    # Vector database configuration
    VECTOR_DB_URL = _config.get('vector_db', {}).get('url', "http://localhost:8080")
    VECTOR_DB_GRPC_PORT = _config.get('vector_db', {}).get('grpc_port', 50051)
    
    # LLM configuration
    LLM_API_KEY = _config.get('llm', {}).get('api_key', "your-api-key-here")
    LLM_MODEL = _config.get('llm', {}).get('model', "gpt-3.5-turbo")
    
    # Redis configuration
    REDIS_URL = _config.get('redis', {}).get('url', "redis://localhost:6379/0")
    
    # MinIO configuration
    MINIO_ENDPOINT = _config.get('minio', {}).get('endpoint', "localhost:9000")
    MINIO_ACCESS_KEY = _config.get('minio', {}).get('access_key', "minioadmin")
    MINIO_SECRET_KEY = _config.get('minio', {}).get('secret_key', "minioadmin")
    
    # API configuration
    API_HOST = _config.get('api', {}).get('host', "0.0.0.0")
    API_PORT = _config.get('api', {}).get('port', 8000)
    
    # Embedding configuration
    EMBEDDING_PROVIDER = _config.get('embedding', {}).get('provider', "local_api")
    EMBEDDING_LOCAL_API_URL = _config.get('embedding', {}).get('local_api', {}).get('url', "http://172.16.89.10:10669/scbllm/embedding-infer/embedding")
    EMBEDDING_SILICONFLOW_API_KEY = _config.get('embedding', {}).get('siliconflow', {}).get('api_key', "your-siliconflow-api-key-here")
    EMBEDDING_SILICONFLOW_MODEL_NAME = _config.get('embedding', {}).get('siliconflow', {}).get('model_name', "BAAI/bge-large-zh-v1.5")
    EMBEDDING_SILICONFLOW_API_URL = _config.get('embedding', {}).get('siliconflow', {}).get('api_url', "https://api.siliconflow.cn/v1/embeddings")

    EMBEDDING_API_URL = EMBEDDING_LOCAL_API_URL if EMBEDDING_PROVIDER == "local_api" else EMBEDDING_SILICONFLOW_API_URL