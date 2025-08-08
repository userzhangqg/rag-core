
from abc import ABC, abstractmethod
from typing import List, Union, Dict, Any, Optional
from pathlib import Path

from langchain_core.documents.base import Document
from utils.logger import get_module_logger


class BaseParser(ABC):
    """
    抽象基类，定义所有解析器的通用接口
    使用策略模式，支持按文件类型自动选择解析器
    """
    
    # 支持的文件扩展名列表
    supported_extensions: List[str] = []
    
    def __init__(self, **kwargs):
        self.logger = get_module_logger("parser")
        self.config = kwargs
    
    @abstractmethod
    def parse(self, source: Union[str, bytes], source_type: str = "file") -> List[Document]:
        """
        解析文档内容
        
        Args:
            source: 文件路径、文件内容或字节流
            source_type: "file" | "content" | "bytes"
            
        Returns:
            List[Document]: 解析后的文档列表
        """
        pass
    
    def can_parse(self, file_path: Union[str, Path]) -> bool:
        """
        检查是否可以解析指定文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否支持该文件类型
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        return file_path.suffix.lower() in [ext.lower() for ext in self.supported_extensions]
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        获取文件基本信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict[str, Any]: 文件信息字典
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        try:
            stat = file_path.stat()
            return {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_size": stat.st_size,
                "file_extension": file_path.suffix.lower(),
                "last_modified": stat.st_mtime
            }
        except Exception as e:
            self.logger.warning(f"Failed to get file info for {file_path}: {e}")
            return {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_size": 0,
                "file_extension": file_path.suffix.lower(),
                "last_modified": None
            }