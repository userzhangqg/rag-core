#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Documents API Router
"""

import os
import tempfile
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse

from core.pipeline.rag_pipeline import RAGPipeline, RAGConfig
from utils.logger import setup_logger
from api.models import FileUploadResponse, ErrorResponse

router = APIRouter(prefix="/documents", tags=["documents"])

# Global pipeline instance
_pipeline: Optional[RAGPipeline] = None

def get_pipeline() -> RAGPipeline:
    """获取RAG管道实例"""
    global _pipeline
    if _pipeline is None:
        config = RAGConfig.from_config_file()
        setup_logger(config)
        _pipeline = RAGPipeline(config)
    return _pipeline


@router.post("/upload", response_model=FileUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    pipeline: RAGPipeline = Depends(get_pipeline)
):
    """
    上传并向量化文档
    
    支持多种文档格式：.md, .txt, .pdf等
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    
    # 检查文件扩展名
    allowed_extensions = {'.md', '.txt', '.pdf', '.docx', '.html'}
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件类型。支持的格式：{', '.join(allowed_extensions)}"
        )
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        try:
            # 写入文件内容
            content = await file.read()
            tmp_file.write(content)
            tmp_file.flush()
            
            # 处理文件
            chunks = pipeline.process_file(tmp_file.name)
            
            return FileUploadResponse(
                filename=file.filename,
                chunks_count=len(chunks),
                message=f"文件 '{file.filename}' 已成功处理并向量存储"
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")
        finally:
            # 清理临时文件
            if os.path.exists(tmp_file.name):
                os.unlink(tmp_file.name)


from api.models import TextUploadRequest

@router.post("/upload-text", response_model=FileUploadResponse)
async def upload_text(
    request: TextUploadRequest,
    pipeline: RAGPipeline = Depends(get_pipeline)
):
    """
    上传文本内容并向量存储
    """
    try:
        chunks = pipeline.process_content(request.content, request.source_name)
        return FileUploadResponse(
            filename=request.source_name,
            chunks_count=len(chunks),
            message=f"文本内容已成功处理并向量存储"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文本处理失败: {str(e)}")


@router.get("/health")
async def check_vector_store_health(
    pipeline: RAGPipeline = Depends(get_pipeline)
):
    """检查向量存储健康状态"""
    try:
        # 简单的健康检查 - 尝试连接向量存储
        info = pipeline.get_pipeline_info()
        return {
            "status": "healthy",
            "vector_store": type(pipeline.vector_store).__name__,
            "retriever": info.get("retriever_type", "unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"向量存储连接失败: {str(e)}")