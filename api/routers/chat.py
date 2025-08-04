#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chat API Router
"""

from typing import Optional
import json

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

from core.pipeline.rag_pipeline import RAGPipeline, RAGConfig
from utils.logger import setup_logger
from api.models import ChatRequest, ChatResponse, ErrorResponse

router = APIRouter(prefix="/chat", tags=["chat"])

# Global pipeline instance
_pipeline: Optional[RAGPipeline] = None

def get_pipeline() -> RAGPipeline:
    """获取RAG管道实例"""
    global _pipeline
    if _pipeline is None:
        config = RAGConfig.from_config_file()
        # 配置日志级别
        config.logging_config.module_levels['llm'] = 'INFO'
        setup_logger(config)
        _pipeline = RAGPipeline(config)
    return _pipeline


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    pipeline: RAGPipeline = Depends(get_pipeline)
):
    """
    基于RAG的对话查询
    
    使用上传的文档作为知识库进行问答
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="查询内容不能为空")
    
    try:
        # 执行RAG查询
        response = pipeline.query(
            query_text=request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            use_rerank=request.use_rerank,
            generate_streaming=False
        )
        
        return ChatResponse(
            response=response,
            message="查询成功"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询处理失败: {str(e)}")


@router.post("/query-stream")
async def chat_query_stream(
    request: ChatRequest,
    pipeline: RAGPipeline = Depends(get_pipeline)
):
    """
    基于RAG的流式对话查询
    
    返回流式响应，逐字生成回答
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="查询内容不能为空")
    
    try:
        # 执行RAG查询（流式）
        response_generator = pipeline.query(
            query_text=request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            use_rerank=request.use_rerank,
            generate_streaming=True
        )
        
        async def generate_stream():
            """生成流式响应"""
            try:
                for chunk in response_generator:
                    if chunk:
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"流式查询处理失败: {str(e)}")


@router.get("/health")
async def check_chat_health(
    pipeline: RAGPipeline = Depends(get_pipeline)
):
    """检查对话系统健康状态"""
    try:
        # 检查各组件状态
        info = pipeline.get_pipeline_info()
        return {
            "status": "healthy",
            "llm_type": info.get("llm_type", "unknown"),
            "reranker_type": info.get("reranker_type", "unknown"),
            "prompt_engine": info.get("prompt_engine_type", "unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"对话系统检查失败: {str(e)}")