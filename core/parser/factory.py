#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Parser Factory Module for RAG Core System
支持按文件类型自动选择解析器的工厂类，支持文本内容智能解析
"""

from typing import Optional, Dict, Type, List, Union
from pathlib import Path
import importlib

from core.parser.base import BaseParser
from core.parser.pdf_simple_parser import PdfSimpleParser
from core.parser.pdf_mineru_parser import MineruVLMParser, MineruPipelineParser
from core.parser.markdown_parser import MarkdownParser
from core.parser.html_parser import HtmlParser
from core.parser.text_parser import TextParser
from core.parser.content_detector import ContentDetector


class ParserFactory:
    """
    增强型Parser工厂类，支持按文件类型自动选择解析器
    使用策略模式和工厂模式，支持动态扩展
    """
    
    # 文件扩展名到解析器类的映射
    _parser_registry: Dict[str, Type[BaseParser]] = {}
    
    # 默认解析器配置
    _default_parsers = {
        ".pdf": {
            "fast": PdfSimpleParser,
            "mineru_vlm": MineruVLMParser,
            "mineru_pipeline": MineruPipelineParser
        },
        ".md": {
            "default": MarkdownParser
        },
        ".markdown": {
            "default": MarkdownParser
        },
        ".html": {
            "default": HtmlParser
        },
        ".htm": {
            "default": HtmlParser
        },
        ".txt": {
            "default": TextParser
        },
        ".text": {
            "default": TextParser
        }
    }
    
    _global_config = {}
    
    @classmethod
    def initialize_config(cls, **config):
        """初始化全局配置"""
        cls._global_config = config
    
    @classmethod
    def register_parser(cls, file_extension: str, parser_class: Type[BaseParser], 
                       parser_name: str = "default") -> None:
        """
        注册新的解析器到工厂
        
        Args:
            file_extension: 文件扩展名（如".pdf"）
            parser_class: 解析器类
            parser_name: 解析器名称（用于同一扩展名的多个解析器选择）
        """
        file_extension = file_extension.lower()
        
        if file_extension not in cls._parser_registry:
            cls._parser_registry[file_extension] = {}
        
        cls._parser_registry[file_extension][parser_name] = parser_class
        
        # 同时更新支持的扩展名
        if hasattr(parser_class, 'supported_extensions'):
            for ext in parser_class.supported_extensions:
                if ext.lower() not in cls._parser_registry:
                    cls._parser_registry[ext.lower()] = {}
                cls._parser_registry[ext.lower()][parser_name] = parser_class
    
    @classmethod
    def _initialize_registry(cls) -> None:
        """初始化解析器注册表"""
        if not cls._parser_registry:
            for ext, parsers in cls._default_parsers.items():
                cls._parser_registry[ext] = parsers
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """
        获取所有支持的文件扩展名
        
        Returns:
            List[str]: 支持的扩展名列表
        """
        cls._initialize_registry()
        return list(cls._parser_registry.keys())
    
    @classmethod
    def get_parser_for_extension(cls, file_extension: str, 
                                parser_type: Optional[str] = None) -> Type[BaseParser]:
        """
        根据文件扩展名获取对应的解析器类
        
        Args:
            file_extension: 文件扩展名
            parser_type: 解析器类型（可选）
            
        Returns:
            Type[BaseParser]: 解析器类
            
        Raises:
            ValueError: 当找不到对应的解析器时
        """
        cls._initialize_registry()
        
        file_extension = file_extension.lower()
        
        if file_extension not in cls._parser_registry:
            raise ValueError(
                f"Unsupported file extension: {file_extension}. "
                f"Supported extensions: {list(cls._parser_registry.keys())}"
            )
        
        parsers = cls._parser_registry[file_extension]
        
        if parser_type and parser_type in parsers:
            return parsers[parser_type]
        elif "default" in parsers:
            return parsers["default"]
        elif len(parsers) == 1:
            return list(parsers.values())[0]
        else:
            # 如果有多个解析器但没有指定类型，使用第一个可用的
            return list(parsers.values())[0]
    
    @classmethod
    def create_parser(cls, file_path: Union[str, Path], 
                     parser_type: Optional[str] = None,
                     **kwargs) -> BaseParser:
        """
        根据文件路径和配置创建对应的解析器实例
        
        Args:
            file_path: 文件路径
            parser_type: 解析器类型（如"fast", "mineru"等）
            **kwargs: 传递给解析器的额外参数
            
        Returns:
            BaseParser: 解析器实例
            
        Raises:
            ValueError: 当文件类型不支持或找不到解析器时
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        file_extension = file_path.suffix.lower()
        
        # 映射旧的parser_type到新的类型
        parser_type_mapping = {
            "fast": "fast",
            "mineru": "mineru_vlm",
            "mineru_vlm": "mineru_vlm",
            "mineru_pipeline": "mineru_pipeline"
        }
        
        if parser_type in parser_type_mapping:
            parser_type = parser_type_mapping[parser_type]
        
        parser_class = cls.get_parser_for_extension(file_extension, parser_type)
        
        # 为特定解析器添加配置参数
        if file_extension == ".pdf":
            if parser_class == MineruVLMParser:
                kwargs.setdefault("backend", "vlm-sglang-client")
            elif parser_class == MineruPipelineParser:
                kwargs.setdefault("backend", "pipeline")
        
        return parser_class(**kwargs)
    
    @classmethod
    def auto_detect_parser(cls, file_path: Union[str, Path], 
                          config: Optional[Dict] = None) -> BaseParser:
        """
        自动检测文件类型并创建对应的解析器
        
        Args:
            file_path: 文件路径
            config: 配置字典，包含解析器选择参数
            
        Returns:
            BaseParser: 解析器实例
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        config = config or cls._global_config
        
        file_extension = file_path.suffix.lower()
        
        # 根据文件类型和配置选择解析器
        if file_extension == ".pdf":
            parser_type = config.get("pdf_parser_type", "fast")
        elif file_extension in [".md", ".markdown"]:
            parser_type = "default"
        else:
            parser_type = "default"
        
        return cls.create_parser(file_path, parser_type, **config)

    @classmethod
    def smart_select_parser(cls, file_path: Union[str, Path], 
                           content: Optional[str] = None,
                           config: Optional[Dict] = None) -> BaseParser:
        """
        智能内容类型选择解析器
        
        Args:
            file_path: 文件路径
            content: 文件内容预览（可选，用于内容特征分析）
            config: 配置字典，包含解析器选择参数
            
        Returns:
            BaseParser: 智能选择的解析器实例
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        config = config or cls._global_config
        
        # 优先使用文件扩展名选择解析器
        file_extension = file_path.suffix.lower()
        
        # 如果提供了内容，进行内容特征分析
        if content:
            # 检测内容特征
            detector = ContentDetector()
            content_type = detector.detect_content_type(content)
            
            # 根据内容特征调整解析器选择
            if content_type == "markdown" and file_extension not in [".md", ".markdown"]:
                # 内容看起来是markdown但扩展名不是
                return cls.create_parser(file_path, "default", **config)
            elif content_type == "html" and file_extension not in [".html", ".htm"]:
                # 内容看起来是HTML但扩展名不是
                return cls.create_parser(file_path, "default", **config)
        
        # 回退到基于扩展名的选择
        return cls.auto_detect_parser(file_path, config)
    
    @classmethod
    def register_future_parsers(cls):
        """
        为未来扩展的解析器预留注册接口
        可以在这里添加doc、xlsx、pptx、html等解析器
        """
        try:
            from core.parser.docx_parser import DocxParser
            cls.register_parser(".docx", DocxParser)
        except ImportError:
            pass
            
        try:
            from core.parser.excel_parser import ExcelParser
            cls.register_parser(".xlsx", ExcelParser)
        except ImportError:
            pass
            
        try:
            from core.parser.powerpoint_parser import PowerPointParser
            cls.register_parser(".pptx", PowerPointParser)
        except ImportError:
            pass
            
        try:
            from core.parser.html_parser import HtmlParser
            cls.register_parser(".html", HtmlParser)
        except ImportError:
            pass
            
        try:
            from core.parser.text_parser import TextParser
            cls.register_parser(".txt", TextParser)
        except ImportError:
            pass


    @classmethod
    def create_smart_parser_for_content(cls, content: str, 
                                      parser_type: Optional[str] = None,
                                      **kwargs) -> BaseParser:
        """
        根据内容特征智能选择解析器
        
        Args:
            content: 文本内容
            parser_type: 强制指定解析器类型（可选）
            **kwargs: 传递给解析器的额外参数
            
        Returns:
            BaseParser: 智能选择的解析器实例
        """
        if parser_type:
            # 强制使用指定解析器
            if parser_type == "markdown":
                return MarkdownParser(**kwargs)
            elif parser_type == "html":
                return HtmlParser(**kwargs)
            elif parser_type == "text":
                return TextParser(**kwargs)
            else:
                raise ValueError(f"Unsupported parser type: {parser_type}")
        
        # 智能选择解析器
        content_type = ContentDetector.select_parser_type(content)
        
        if content_type == "markdown":
            return MarkdownParser(**kwargs)
        elif content_type == "html":
            return HtmlParser(**kwargs)
        else:
            return TextParser(**kwargs)

    @classmethod
    def get_parser_info(cls) -> Dict[str, List[str]]:
        """
        获取所有支持的解析器信息
        
        Returns:
            Dict[str, List[str]]: 文件扩展名到解析器名称的映射
        """
        cls._initialize_registry()
        
        info = {}
        for ext, parsers in cls._parser_registry.items():
            info[ext] = list(parsers.keys())
        
        return info


# 自动注册所有解析器
ParserFactory._initialize_registry()
ParserFactory.register_future_parsers()