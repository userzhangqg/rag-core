"""
RAG流程单元测试
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

import sys
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.pipeline.rag_pipeline import RAGPipeline
from core.pipeline.preprocessing_pipeline import DocumentProcessingPipeline as PreprocessingPipeline, RAGConfig, DocumentProcessingPipelineBuilder as PreprocessingPipelineBuilder
from core.chunking.recursive_char_text_chunk import RecursiveCharTextChunk


class TestRAGConfig:
    """测试RAG配置类"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = RAGConfig()
        assert config.chunk_size == 1000
        assert config.chunk_overlap == 200
        assert config.separators is None
        assert config.remove_hyperlinks is False
        assert config.remove_images is False
        assert config.enable_metadata is True
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = RAGConfig(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n", " ", ""],
            remove_hyperlinks=True,
            remove_images=True,
            enable_metadata=False
        )
        assert config.chunk_size == 500
        assert config.chunk_overlap == 100
        assert config.separators == ["\n", " ", ""]
        assert config.remove_hyperlinks is True
        assert config.remove_images is True
        assert config.enable_metadata is False


class TestRAGPipeline:
    """测试RAG流程管道"""
    
    def setup_method(self):
        """测试前设置"""
        self.pipeline = RAGPipeline()
    
    def test_pipeline_initialization(self):
        """测试管道初始化"""
        assert self.pipeline.config.chunk_size == 1000
        assert self.pipeline.config.chunk_overlap == 200
        # 检查新RAGPipeline的组件
        assert hasattr(self.pipeline, 'preprocessing_pipeline')
        assert hasattr(self.pipeline, 'retriever')
        assert hasattr(self.pipeline, 'llm')
        assert hasattr(self.pipeline, 'prompt_engine')
        
        # 检查预处理管道
        assert isinstance(self.pipeline.preprocessing_pipeline, PreprocessingPipeline)
    
    def test_process_content_empty(self):
        """测试处理空内容"""
        chunks = self.pipeline.process_content("")
        assert chunks == []
    
    def test_process_content_simple(self):
        """测试处理简单内容"""
        content = "这是一个简单的测试内容。"
        chunks = self.pipeline.process_content(content)
        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)
        assert all('metadata' in chunk for chunk in chunks)
    
    def test_process_content_with_metadata(self):
        """测试处理带元数据的内容"""
        content = "测试内容"
        custom_metadata = {"author": "test", "version": "1.0"}
        chunks = self.pipeline.process_content(content, custom_metadata=custom_metadata)
        
        for chunk in chunks:
            assert chunk['metadata']['author'] == "test"
            assert chunk['metadata']['version'] == "1.0"
    
    def test_process_file_not_found(self):
        """测试处理不存在的文件"""
        with pytest.raises(FileNotFoundError):
            self.pipeline.process_file("non_existent_file.md")
    
    def test_process_file_success(self):
        """测试成功处理文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# 测试\n这是一个测试文件。")
            temp_path = f.name
        
        try:
            chunks = self.pipeline.process_file(temp_path)
            assert len(chunks) > 0
            assert any(temp_path in chunk['metadata']['source_file'] for chunk in chunks)
        finally:
            os.unlink(temp_path)
    
    def test_process_directory_empty(self):
        """测试处理空目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            results = self.pipeline.process_directory(temp_dir)
            assert results == {}
    
    def test_process_directory_with_files(self):
        """测试处理包含文件的目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试文件
            file1_path = os.path.join(temp_dir, "test1.md")
            file2_path = os.path.join(temp_dir, "test2.md")
            
            with open(file1_path, 'w') as f:
                f.write("# 文件1\n内容1")
            
            with open(file2_path, 'w') as f:
                f.write("# 文件2\n内容2")
            
            results = self.pipeline.process_directory(temp_dir)
            
            assert len(results) == 2
            assert file1_path in results
            assert file2_path in results
            assert len(results[file1_path]) > 0
            assert len(results[file2_path]) > 0
    
    def test_get_pipeline_info(self):
        """测试获取管道信息"""
        info = self.pipeline.get_pipeline_info()
        assert "preprocessing_config" in info
        assert "retriever_type" in info
        assert "llm_type" in info
        assert "prompt_engine_type" in info
        
        # 检查组件类型
        assert info["retriever_type"] == "VectorRetriever"
        assert info["llm_type"] == "LocalAPILLM"
        assert info["prompt_engine_type"] == "PromptEngine"
    
    def test_update_config(self):
        """测试更新配置"""
        original_size = self.pipeline.config.chunk_size
        self.pipeline.update_config(chunk_size=500)
        assert self.pipeline.config.chunk_size == 500
        assert self.pipeline.preprocessing_pipeline.chunker.chunk_size == 500
    
    def test_query_method_exists(self):
        """测试查询方法是否存在"""
        # 检查是否存在query方法
        assert hasattr(self.pipeline, 'query')
        assert callable(getattr(self.pipeline, 'query'))


class TestPreprocessingPipelineBuilder:
    """测试预处理流程构建器"""
    
    def test_create_default_pipeline(self):
        """测试创建默认管道"""
        pipeline = PreprocessingPipelineBuilder.create_default_pipeline()
        assert isinstance(pipeline, PreprocessingPipeline)
        assert pipeline.config.chunk_size == 1000
    
    def test_create_academic_pipeline(self):
        """测试创建学术文档管道"""
        pipeline = PreprocessingPipelineBuilder.create_academic_pipeline()
        assert isinstance(pipeline, PreprocessingPipeline)
        assert pipeline.config.chunk_size == 800
        assert pipeline.config.remove_hyperlinks is True
    
    def test_create_tech_doc_pipeline(self):
        """测试创建技术文档管道"""
        pipeline = PreprocessingPipelineBuilder.create_tech_doc_pipeline()
        assert isinstance(pipeline, PreprocessingPipeline)
        assert pipeline.config.chunk_size == 1200


class TestRecursiveCharTextChunk:
    """测试递归字符分块器"""
    
    def test_initialization(self):
        """测试初始化"""
        chunker = RecursiveCharTextChunk(chunk_size=500, chunk_overlap=100)
        assert chunker.chunk_size == 500
        assert chunker.chunk_overlap == 100
    
    def test_invalid_overlap(self):
        """测试无效的重叠大小"""
        with pytest.raises(ValueError, match="chunk_overlap必须小于chunk_size"):
            RecursiveCharTextChunk(chunk_size=100, chunk_overlap=200)
    
    def test_get_chunks_empty(self):
        """测试空文本分块"""
        chunker = RecursiveCharTextChunk()
        chunks = chunker.get_chunks("")
        assert chunks == []
    
    def test_get_chunks_simple(self):
        """测试简单文本分块"""
        chunker = RecursiveCharTextChunk(chunk_size=50, chunk_overlap=10)
        text = "这是一个测试文本，用于测试分块功能。"
        chunks = chunker.get_chunks(text)
        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)
        assert all('metadata' in chunk for chunk in chunks)
    
    def test_get_chunks_with_custom_size(self):
        """测试使用自定义分块大小"""
        chunker = RecursiveCharTextChunk(chunk_size=100, chunk_overlap=20)
        text = "这是一个测试文本，用于测试分块功能。"
        chunks = chunker.get_chunks(text, chunk_size=50)
        assert len(chunks) > 0
        # 验证是否使用了自定义大小
        for chunk in chunks:
            assert len(chunk['text']) <= 50
    
    def test_get_chunk_info(self):
        """测试获取分块器信息"""
        chunker = RecursiveCharTextChunk()
        info = chunker.get_chunk_info()
        assert info["type"] == "RecursiveCharTextChunk"
        assert "chunk_size" in info
        assert "chunk_overlap" in info


if __name__ == "__main__":
    pytest.main([__file__])