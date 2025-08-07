#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG Pipeline Module for RAG Core System
"""

from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from core.pipeline.preprocessing_pipeline import DocumentProcessingPipeline as PreprocessingPipeline, RAGConfig
from utils.logger import get_module_logger
from core.retrieval.factory import RetrievalFactory
from core.llm.factory import LLMFactory
from core.reranker.factory import RerankerFactory
from core.prompt.engine import PromptEngine
from core.parser.factory import ParserFactory


class RAGPipeline:
    """
    RAG流程管道
    
    集成预处理、检索和生成，提供完整的RAG流程。
    """
    
    def __init__(self, config: Optional[RAGConfig] = None):
        """
        初始化RAG流程管道
        
        Args:
            config: RAG配置参数
        """
        self.config = config or RAGConfig.from_config_file()
        self.logger = get_module_logger("RAGPipeline")
        
        self.logger.info("Starting RAG pipeline initialization...")
        
        # 初始化预处理管道
        self.logger.debug("Initializing preprocessing pipeline...")
        self.preprocessing_pipeline = PreprocessingPipeline(self.config)
        
        # 初始化解析器
        # self.logger.debug("Initializing parser...")
        # self.parser = ParserFactory.create_parser(
        #     parser_type=self.config.parser_type,
        #     mineru_parser_backend=self.config.mineru_parser_backend
        # )
        
        # 初始化向量存储
        self.logger.debug("Initializing vector store...")
        self.vector_store = self.preprocessing_pipeline.vector
        
        # 初始化检索器
        self.logger.debug(f"Initializing retriever: {self.config.retrieval_type}")
        self.retriever = RetrievalFactory.create_retriever(
            retriever_type=self.config.retrieval_type,
            vector_store=self.vector_store,
            hybrid_config=self.config.hybrid_config
        )
        self.logger.info(f"Using {type(self.retriever).__name__}")
        
        # 初始化LLM
        self.logger.debug(f"Initializing LLM: {self.config.llm_provider}")
        self.llm = LLMFactory.create_llm(
            provider=self.config.llm_provider,
            api_key=self.config.llm_api_key,
            model_name=self.config.llm_model_name,
            api_url=self.config.llm_api_url
        )
        
        # 初始化Reranker
        self.logger.debug(f"Initializing reranker: {self.config.rerank_provider}")
        self.reranker = RerankerFactory.create_reranker(
            provider=self.config.rerank_provider,
            api_url=self.config.rerank_api_url
        )
        
        # 初始化Prompt引擎
        self.logger.debug("Initializing prompt engine...")
        self.prompt_engine = PromptEngine()
        
        self.logger.info("RAG pipeline initialization completed successfully")
    
    def process_file(
        self, 
        file_path: Union[str, Path],
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        处理单个markdown文件
        
        Args:
            file_path: 文件路径
            custom_metadata: 自定义元数据
            
        Returns:
            List[Dict[str, Any]]: 分块后的文本列表，每个包含text和metadata
        """
        return self.preprocessing_pipeline.process_file(file_path, custom_metadata)
    
    def process_content(
        self,
        content: str,
        source_name: str = "content",
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        处理文本内容
        
        Args:
            content: 文本内容
            source_name: 来源名称
            custom_metadata: 自定义元数据
            
        Returns:
            List[Dict[str, Any]]: 分块后的文本列表
        """
        return self.preprocessing_pipeline.process_content(content, source_name, custom_metadata)
    
    def process_directory(
        self,
        directory: Union[str, Path],
        file_pattern: str = "*.md",
        recursive: bool = True,
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量处理目录中的markdown文件
        
        Args:
            directory: 目录路径
            file_pattern: 文件匹配模式
            recursive: 是否递归子目录
            custom_metadata: 自定义元数据
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 文件路径到分块列表的映射
        """
        return self.preprocessing_pipeline.process_directory(directory, file_pattern, recursive, custom_metadata)
    
    def query(self, query_text: str, top_k: int = None, score_threshold: float = 0.0, use_rerank: bool = True, generate_streaming: bool = False) -> str:
        """
        查询并生成回答
        
        Args:
            query_text: 查询文本
            top_k: 返回的检索结果数量
            score_threshold: 最小相似度分数
            use_rerank: 是否使用rerank
            
        Returns:
            生成的回答文本
        """
        self.logger.info(f"Starting RAG query: '{query_text[:50]}...'")
        
        # 使用配置文件中的默认值
        if top_k is None:
            top_k = self.config.retrieve_top_k
        
        self.logger.debug(f"Query parameters - top_k: {top_k}, score_threshold: {score_threshold}, use_rerank: {use_rerank}")

        
        # 检索相关文档
        self.logger.debug(f"Searching for relevant documents using {self.config.retrieval_type} search...")
        retrieved_docs = self.retriever.search(query_text, top_k, score_threshold)
        self.logger.info(f"Retrieved {len(retrieved_docs)} documents using {self.config.retrieval_type} search")
        
        # 提取文档文本
        contexts = [doc['text'] for doc in retrieved_docs]
        self.logger.debug(f"Extracted {len(contexts)} contexts from retrieved documents")
        self.logger.debug(f"Top {top_k} Contexts: {retrieved_docs[:top_k]}")
        
        # 如果启用rerank，则对检索结果进行重排序
        if use_rerank and len(contexts) > 1:
            self.logger.debug("Applying reranker to contexts...")
            contexts = self.reranker.rerank(query_text, contexts)
            contexts = contexts[:self.config.rerank_top_n]
            self.logger.info(f"Reranked contexts, final count: {len(contexts)}")
            self.logger.debug(f"Reranked contexts: {contexts}")
        else:
            self.logger.debug("Skipping reranker, use_rerank is False")
            contexts = contexts[:top_k]

        # TODO： filter重复文本使用hash值或uuid
        
        # 构建Prompt
        self.logger.debug("Building prompt for LLM...")
        prompt = self.prompt_engine.build_prompt(query_text, contexts)
        self.logger.debug(f"Generated prompt with {len(prompt)} characters")
        
        # 生成回答
        self.logger.debug("Generating response from LLM...")
        response = self.llm.generate(prompt, streaming=generate_streaming)
        
        # 处理流式和非流式响应
        if generate_streaming:
            # 流式响应，返回生成器
            self.logger.info("Returning streaming response generator")
            return response
        else:
            # 非流式响应，记录长度
            self.logger.info(f"Generated response with {len(response)} characters")
            return response
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """获取管道配置信息"""
        return {
            "preprocessing_config": self.preprocessing_pipeline.get_pipeline_info(),
            "retriever_type": type(self.retriever).__name__,
            "llm_type": type(self.llm).__name__,
            "reranker_type": type(self.reranker).__name__,
            "prompt_engine_type": type(self.prompt_engine).__name__
        }
    
    def update_config(self, **kwargs) -> None:
        """
        动态更新配置
        
        Args:
            **kwargs: 配置参数
        """
        # 更新RAGPipeline的配置
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                self.logger.info(f"更新RAG配置: {key} = {value}")
        
        # 更新预处理管道的配置
        self.preprocessing_pipeline.update_config(**kwargs)
        
        # 重新初始化LLM
        self.llm = LLMFactory.create_llm(
            provider=self.config.llm_provider,
            api_key=self.config.llm_api_key,
            model_name=self.config.llm_model_name,
            api_url=self.config.llm_api_url
        )
        
        # 重新初始化Reranker
        self.reranker = RerankerFactory.create_reranker(
            provider=self.config.rerank_provider,
            api_url=self.config.rerank_api_url
        )