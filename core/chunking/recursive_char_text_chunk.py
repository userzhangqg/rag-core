from typing import List, Optional, Union
from langchain.text_splitter import RecursiveCharacterTextSplitter as LangChainRecursiveSplitter
from langchain_core.documents import Document as LangChainDocument
from core.chunking.base import BaseChunker


class RecursiveCharTextChunk(BaseChunker):
    """
    递归字符文本分块器
    
    基于langchain的RecursiveCharacterTextSplitter实现，
    支持递归使用不同分隔符进行文本分块，并提供重叠窗口功能。
    
    特点：
    1. 支持多种分隔符的递归分割
    2. 支持重叠窗口，保持上下文连贯性
    3. 继承BaseChunker，便于扩展
    4. 与langchain生态兼容

    TODO:
    1. 支持因chunk_size过大导致的分块被一起召回
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None,
        length_function=None,
        keep_separator: bool = True,
        add_start_index: bool = False,
        strip_whitespace: bool = True
    ):
        """
        初始化递归字符文本分块器
        
        Args:
            chunk_size: 每个分块的最大字符数
            chunk_overlap: 相邻分块之间的重叠字符数
            separators: 用于分割的分隔符列表，按优先级排序
            length_function: 计算文本长度的函数
            keep_separator: 是否在分块中保留分隔符
            add_start_index: 是否在元数据中记录分块的起始位置
            strip_whitespace: 是否去除分块两端的空白字符
        """
        super().__init__()
        
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap should be smaller than chunk_size")
            
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""]
        
        # 设置默认长度函数
        if length_function is None:
            length_function = len
            
        # 创建langchain分词器
        self._langchain_splitter = LangChainRecursiveSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=self.separators,
            length_function=length_function,
            is_separator_regex=False,
            keep_separator=keep_separator,
            add_start_index=add_start_index,
            strip_whitespace=strip_whitespace
        )
    
    def get_chunks(
        self, 
        paragraphs: Union[str, List[str]], 
        chunk_size: Optional[int] = None,
        metadata: Optional[dict] = None
    ) -> List[dict]:
        """
        将文本分割成重叠的分块
        
        Args:
            paragraphs: 输入文本或文本列表
            chunk_size: 覆盖默认的chunk_size
            metadata: 附加到每个分块的元数据
            
        Returns:
            List[dict]: 分块列表，每个分块包含text和metadata字段
        """
        if chunk_size is not None:
            # 临时修改chunk_size
            original_chunk_size = self.chunk_size
            self.chunk_size = chunk_size
            self._langchain_splitter.chunk_size = chunk_size
        
        try:
            if isinstance(paragraphs, str):
                paragraphs = [paragraphs]
            
            all_chunks = []
            
            for idx, text in enumerate(paragraphs):
                if not text.strip():
                    continue
                    
                # 使用langchain进行分块
                docs = self._langchain_splitter.create_documents([text])
                
                for doc_idx, doc in enumerate(docs):
                    chunk_data = {
                        "text": doc.page_content,
                        "metadata": {
                            "chunk_index": doc_idx,
                            "source_index": idx,
                            "chunk_size": len(doc.page_content),
                            **(metadata or {})
                        }
                    }
                    
                    # 添加起始位置信息（如果启用）
                    if hasattr(doc, "metadata") and "start_index" in doc.metadata:
                        chunk_data["metadata"]["start_char"] = doc.metadata["start_index"]
                    
                    all_chunks.append(chunk_data)
            
            return all_chunks
            
        finally:
            # 恢复原始chunk_size
            if chunk_size is not None:
                self.chunk_size = original_chunk_size
                self._langchain_splitter.chunk_size = original_chunk_size
    
    def split_documents(
        self, 
        documents: List[LangChainDocument],
        metadata: Optional[dict] = None
    ) -> List[LangChainDocument]:
        """
        分割langchain文档对象
        
        Args:
            documents: langchain文档列表
            metadata: 附加元数据
            
        Returns:
            List[LangChainDocument]: 分割后的文档列表
        """
        return self._langchain_splitter.split_documents(documents)
    
    def get_chunk_info(self) -> dict:
        """获取分块器配置信息"""
        return {
            "type": "RecursiveCharTextChunk",
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "separators": self.separators,
            "total_separators": len(self.separators)
        }