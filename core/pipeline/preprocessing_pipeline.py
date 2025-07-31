import warnings

# Suppress Protobuf warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf.runtime_version")

from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass

from conf.config import RAGConfig

from langchain_core.documents import Document as LangChainDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

from core.parser.markdown_parser import MarkdownParser
from core.chunking.recursive_char_text_chunk import RecursiveCharTextChunk
from core.vector.weaviate_vector import WeaviateVector
from core.embedding.base import EmbeddingBase
from core.embedding.local_api_embedding import LocalAPIEmbedding
from core.embedding.sijiblob_embedding import SiliconFlowEmbedding
from conf.config import RAGConfig
from utils.logger import get_module_logger
    

class DocumentProcessingPipeline:
    """
    文档处理管道
    
    集成markdown解析和递归字符分块，提供完整的文档预处理流程。
    支持文件解析、文本分块、元数据管理、向量化等核心功能。
    """
    
    def __init__(self, config: Optional[RAGConfig] = None):
        """
        初始化RAG流程管道
        
        Args:
            config: RAG配置参数
        """
        self.config = config or RAGConfig.from_config_file()
        self.logger = get_module_logger("DocumentProcessingPipeline")
        
        self.logger.info("Initializing DocumentProcessingPipeline...")
        
        # 初始化组件
        self.logger.debug("Initializing MarkdownParser...")
        self.parser = MarkdownParser(
            remove_hyperlinks=self.config.remove_hyperlinks,
            remove_images=self.config.remove_images
        )
        
        self.logger.debug("Initializing RecursiveCharTextChunk...")
        self.chunker = RecursiveCharTextChunk(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=self.config.separators or ["\n\n", "\n", " ", ""],
            add_start_index=self.config.enable_metadata,
            strip_whitespace=True
        )
        
        # 初始化向量化组件
        self.logger.debug(f"Initializing embedding provider: {self.config.embedding_provider}")
        if self.config.embedding_provider == "siliconflow":
            api_key = self.config.embedding_api_key or "your_api_key_here"
            model_name = self.config.embedding_model_name or "BAAI/bge-large-zh-v1.5"
            self.embedding = SiliconFlowEmbedding(api_key=api_key, model_name=model_name)
            self.logger.info(f"Using SiliconFlow embedding: {model_name}")
        elif self.config.embedding_provider == "local_api":
            api_url = getattr(self.config, 'embedding_api_url', None)
            self.embedding = LocalAPIEmbedding(api_url=api_url)
            self.logger.info("Using local API embedding")
        else:
            raise ValueError(f"Unsupport Embedding Provider: {self.config.embedding_provider}")
        
        # 获取向量数据库URL
        vector_db_url = self.config.vector_db_url
        if vector_db_url is None:
            # 从配置文件中读取默认URL
            vector_db_url = RAGConfig.from_config_file().vector_db_url
        
        self.logger.debug(f"Initializing WeaviateVector with URL: {vector_db_url}")
        self.vector = WeaviateVector(embedding_model=self.embedding, weaviate_url=vector_db_url)
        
        self.logger.info("DocumentProcessingPipeline initialized successfully")
    
    def __del__(self):
        """Destructor to close the Weaviate client connection."""
        if hasattr(self, 'vector'):
            self.vector.close()
    
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
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            self.logger.info(f"Starting to process file: {file_path}")
            
            # 根据配置选择解析方式
            if self.config.parse_by_chapter:
                documents = self.parser.parse_with_sections(str(file_path), source_type="file")
            else:
                documents = self.parser.parse(str(file_path), source_type="file")
            
            if not documents:
                self.logger.warning(f"File content is empty: {file_path}")
                return []
            
            all_chunks = []
            
            # 对每个document单独处理，保持结构完整性
            for doc_idx, document in enumerate(documents):
                if not document.page_content.strip():
                    continue
                
                # 构建基础元数据
                base_metadata = {
                    "source_file": str(file_path),
                    "file_name": file_path.name,
                    "file_size": file_path.stat().st_size,
                    "document_index": doc_idx,
                    "document_type": document.metadata.get("category", "text"),
                    **(custom_metadata or {}),
                    **document.metadata
                }
                
                # 分块处理
                chunks = self.chunker.get_chunks(
                    paragraphs=document.page_content,
                    metadata=base_metadata
                )
                all_chunks.extend(chunks)
            
            chunks = all_chunks
            
            method = "chapter" if self.config.parse_by_chapter else "element"
            self.logger.info(f"File processing completed: {file_path} -> Parsed with {method} into {len(documents)} documents -> {len(chunks)} chunks")
            
            # 向量化处理
            if hasattr(self, 'vector') and chunks:
                texts = [chunk['text'] for chunk in chunks]
                metadata = [chunk['metadata'] for chunk in chunks]
                self.vector.store_texts(texts, metadata)
                self.logger.info(f"Vectorization completed: {len(texts)} texts stored in vector database")
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Failed to process file {file_path}: {str(e)}")
            raise
    
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
        try:
            self.logger.info(f"Starting to process content: {source_name}")
            
            if not content.strip():
                self.logger.warning("Content is empty")
                return []
            
            # 根据配置选择解析方式
            if self.config.parse_by_chapter:
                documents = self.parser.parse_with_sections(content, source_type="content")
            else:
                documents = self.parser.parse(content, source_type="content")
            
            if not documents:
                self.logger.warning("Content is empty")
                return []
            
            all_chunks = []
            
            # 对每个document单独处理
            for doc_idx, document in enumerate(documents):
                if not document.page_content.strip():
                    continue
                
                # 构建元数据
                base_metadata = {
                    "source": source_name,
                    "document_index": doc_idx,
                    "document_type": document.metadata.get("category", "text"),
                    **(custom_metadata or {})
                }
                
                # 分块处理
                chunks = self.chunker.get_chunks(
                    paragraphs=document.page_content,
                    metadata=base_metadata
                )
                all_chunks.extend(chunks)
            
            chunks = all_chunks
            
            method = "chapter" if self.config.parse_by_chapter else "element"
            self.logger.info(f"Content processing completed: {source_name} -> Parsed with {method} into {len(documents)} documents -> {len(chunks)} chunks")
            
            # 向量化处理
            if hasattr(self, 'vector') and chunks:
                texts = [chunk['text'] for chunk in chunks]
                metadata = [chunk['metadata'] for chunk in chunks]
                self.vector.store_texts(texts, metadata)
                self.logger.info(f"Vectorization completed: {len(texts)} texts stored in vector database")
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Failed to process content: {str(e)}")
            raise
    
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
        try:
            directory = Path(directory)
            if not directory.exists():
                raise FileNotFoundError(f"目录不存在: {directory}")
            
            self.logger.info(f"Starting to process directory: {directory}")
            self.logger.debug(f"Processing parameters - file_pattern: {file_pattern}, recursive: {recursive}")
            
            # 查找文件
            if recursive:
                files = list(directory.rglob(file_pattern))
            else:
                files = list(directory.glob(file_pattern))
            
            self.logger.info(f"Found {len(files)} files matching pattern: {file_pattern}")
            
            if not files:
                self.logger.warning(f"No matching files found: {file_pattern}")
                return {}
            
            results = {}
            successful_files = 0
            failed_files = 0
            
            for idx, file_path in enumerate(files, 1):
                try:
                    self.logger.debug(f"Processing file {idx}/{len(files)}: {file_path}")
                    chunks = self.process_file(file_path, custom_metadata)
                    results[str(file_path)] = chunks
                    successful_files += 1
                    self.logger.debug(f"Successfully processed {file_path} -> {len(chunks)} chunks")
                except Exception as e:
                    failed_files += 1
                    self.logger.error(f"Failed to process file {file_path}: {str(e)}")
                    continue
            
            total_chunks = sum(len(chunks) for chunks in results.values())
            self.logger.info(f"Directory processing completed: {len(files)} files processed, {successful_files} successful, {failed_files} failed -> {total_chunks} total chunks")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to process directory: {str(e)}")
            raise
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """获取管道配置信息"""
        return {
            "parser_config": {
                "type": "MarkdownParser",
                "remove_hyperlinks": self.config.remove_hyperlinks,
                "remove_images": self.config.remove_images
            },
            "chunker_config": self.chunker.get_chunk_info(),
            "enable_metadata": self.config.enable_metadata
        }
    
    def update_config(self, **kwargs) -> None:
        """
        动态更新配置
        
        Args:
            **kwargs: 配置参数
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                self.logger.info(f"Configuration updated: {key} = {value}")
        
        # 重新初始化组件
        self.__init__(self.config)




class DocumentProcessingPipelineBuilder:
    """文档处理流程构建器"""
    
    @staticmethod
    def create_pipeline(config: Optional[RAGConfig] = None) -> DocumentProcessingPipeline:
        """创建文档处理流程管道
        
        Args:
            config: 文档处理配置参数，如果为None则使用默认配置
            
        Returns:
            DocumentProcessingPipeline: 文档处理流程管道实例
        """
        return DocumentProcessingPipeline(config)
    
    @staticmethod
    def create_default_pipeline() -> DocumentProcessingPipeline:
        """创建默认配置的文档处理流程（已废弃，建议使用create_pipeline）"""
        import logging
        logging.warning("create_default_pipeline is deprecated, please use create_pipeline")
        return DocumentProcessingPipeline()
    
    @staticmethod
    def create_academic_pipeline() -> DocumentProcessingPipeline:
        """创建学术文档处理流程（已废弃，建议使用create_pipeline）"""
        import logging
        logging.warning("create_academic_pipeline is deprecated, please use create_pipeline")
        config = RAGConfig(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", ". ", " ", ""],
            remove_hyperlinks=True,
            remove_images=True,
            parse_by_chapter=True
        )
        return DocumentProcessingPipeline(config)
    
    @staticmethod
    def create_tech_doc_pipeline() -> DocumentProcessingPipeline:
        """创建技术文档处理流程（已废弃，建议使用create_pipeline）"""
        import logging
        logging.warning("create_tech_doc_pipeline is deprecated, please use create_pipeline")
        config = RAGConfig(
            chunk_size=1200,
            chunk_overlap=200,
            separators=["\n\n", "\n", "#", "##", "###", " ", ""],
            remove_hyperlinks=False,
            remove_images=False
        )
        return DocumentProcessingPipeline(config)
