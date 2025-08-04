#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG Core API Models
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    filename: str
    chunks_count: int
    status: str = "success"
    message: str


class ChatRequest(BaseModel):
    """对话请求模型"""
    query: str
    top_k: Optional[int] = None
    score_threshold: Optional[float] = 0.0
    use_rerank: Optional[bool] = True
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    """对话响应模型"""
    response: str
    sources: Optional[List[Dict[str, Any]]] = None
    status: str = "success"


class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    version: str = "0.1.0"
    components: Dict[str, str] = {}


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str
    detail: Optional[str] = None
    status: str = "error"


class TextUploadRequest(BaseModel):
    """文本上传请求模型"""
    content: str
    source_name: str = "content"