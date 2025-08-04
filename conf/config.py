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
    format: str = "{time:YYYY-MM-DD HH:mm:ss} [{level}] {message}"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    module_levels: Dict[str, str] = field(default_factory=lambda: {
        # 核心模块
        "parser": "INFO",
        "chunking": "INFO",
        "embedding": "INFO",
        "vector": "INFO", 
        "retrieval": "INFO",
        "reranker": "INFO",
        "PromptEngine": "INFO",
        "llm": "INFO",
        
        # Pipeline模块
        "RAGPipeline": "INFO",
        "DocumentProcessingPipeline": "INFO",
        
        # 默认级别
        "default": "DEBUG"
    })

@dataclass
class HybridRetrieverConfig:
    """
    Configuration class for hybrid retriever.
    
    Attributes:
        vector_weight: Weight for vector retrieval scores in final hybrid score
        text_weight: Weight for full-text retrieval scores in final hybrid score
        enable_text_search: Whether to enable full-text search
        enable_vector_search: Whether to enable vector search
    """
    vector_weight: float = 0.75
    text_weight: float = 0.25
    enable_text_search: bool = True
    enable_vector_search: bool = True


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
    vector_db_grpc_port: int = 50051
    
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
    
    # 混合检索参数
    retrieval_type: str = "hybrid"  # "hybrid", "vector", "text"
    hybrid_config: HybridRetrieverConfig = field(default_factory=HybridRetrieverConfig)
    
    # 日志配置
    logging_config: LoggingConfig = field(default_factory=LoggingConfig)
    # debug_config: DebugConfig = field(default_factory=DebugConfig)
    
    # 数据库配置
    database_url: str = "postgresql://user:password@localhost/rag_core"
    
    # Redis配置
    redis_url: str = "redis://localhost:6379/0"
    
    # MinIO配置
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    
    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    gradio_host: str = api_host
    gradio_port: int = 7860
    
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
        
        # 从配置文件中读取数据库配置
        database_config = _config.get('database', {})
        
        # 从配置文件中读取向量数据库配置
        vector_db_config = _config.get('vector_db', {})
        
        # 从配置文件中读取LLM配置
        llm_config = _config.get('llm', {})
        
        # 从配置文件中读取Redis配置
        redis_config = _config.get('redis', {})
        
        # 从配置文件中读取MinIO配置
        minio_config = _config.get('minio', {})
        
        # 从配置文件中读取API配置
        api_config = _config.get('api', {})
        
        # 从配置文件中读取Embedding配置
        embedding_config = _config.get('embedding', {})

        # 从配置文件中读取混合检索配置
        hybrid_config = _config.get('hybrid_config', {})
        
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
            embedding_provider=embedding_config.get('provider', "local_api"),
            embedding_api_key=embedding_config.get('siliconflow', {}).get('api_key'),
            embedding_model_name=embedding_config.get('siliconflow', {}).get('model_name'),
            embedding_api_url=embedding_config.get('local_api', {}).get('url') if embedding_config.get('provider') == "local_api" else embedding_config.get('siliconflow', {}).get('api_url'),
            vector_db_url=vector_db_config.get('url'),
            vector_db_grpc_port=vector_db_config.get('grpc_port', 50051),
            llm_provider=llm_config.get('provider', "local_api"),
            llm_api_key=llm_config.get('api_key'),
            llm_model_name=llm_config.get('model'),
            llm_api_url=llm_config.get('local_api', {}).get('url'),
            rerank_provider=_config.get('rerank', {}).get('provider', "local_api"),
            rerank_api_url=_config.get('rerank', {}).get('local_api', {}).get('url'),
            retrieve_top_k=rag_config.get('retrieve_top_k', 50),
            rerank_top_n=rag_config.get('rerank_top_n', 5),
            retrieval_type=rag_config.get('retrieval_type', "hybrid"),
            hybrid_config=HybridRetrieverConfig(
                vector_weight=hybrid_config.get('vector_weight', 0.75),
                text_weight=hybrid_config.get('text_weight', 0.25),
                enable_text_search=hybrid_config.get('enable_text_search', True),
                enable_vector_search=hybrid_config.get('enable_vector_search', True)
            ),
            logging_config=LoggingConfig(
                level=logging_config.get('level', 'INFO'),
                console_level=logging_config.get('console_level', 'INFO'),
                file_level=logging_config.get('file_level', 'DEBUG'),
                file=logging_config.get('file', 'logs/rag_core.log'),
                max_file_size=logging_config.get('max_file_size', 10485760),
                backup_count=logging_config.get('backup_count', 5),
                format=logging_config.get('format', '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'),
                date_format=logging_config.get('date_format', '%Y-%m-%d %H:%M:%S'),
                module_levels=logging_config.get('module_levels', {})
            ),
            database_url=database_config.get('url', "postgresql://user:password@localhost/rag_core"),
            redis_url=redis_config.get('url', "redis://localhost:6379/0"),
            minio_endpoint=minio_config.get('endpoint', "localhost:9000"),
            minio_access_key=minio_config.get('access_key', "minioadmin"),
            minio_secret_key=minio_config.get('secret_key', "minioadmin"),
            api_host=api_config.get('host', "0.0.0.0"),
            api_port=api_config.get('port', 8000),
            gradio_host=api_config.get('host', "0.0.0.0"),
            gradio_port=api_config.get('gradio_port', 7860),
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