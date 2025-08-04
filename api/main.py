#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG Core API Main Entry
"""
import os
import sys
# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import configuration
from conf.config import RAGConfig

# Import routers
from api.routers.documents import router as documents_router
from api.routers.chat import router as chat_router

# Create the FastAPI app
app = FastAPI(
    title="RAG Core API",
    description="API for the RAG Core system",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    """Root endpoint for the API."""
    return {
        "message": "Welcome to the RAG Core API",
        "version": "0.1.0",
        "endpoints": {
            "documents": "/documents",
            "chat": "/chat",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for the API."""
    return {
        "status": "healthy",
        "service": "RAG Core API",
        "version": "0.1.0",
        "endpoints": [
            {"path": "/documents/upload", "method": "POST", "description": "Upload and vectorize documents"},
            {"path": "/documents/upload-text", "method": "POST", "description": "Upload text content"},
            {"path": "/chat/query", "method": "POST", "description": "Chat with RAG"},
            {"path": "/chat/query-stream", "method": "POST", "description": "Chat with streaming response"}
        ]
    }


if __name__ == "__main__":
    import uvicorn
    # Get default configuration
    config = RAGConfig.from_config_file()
    uvicorn.run(
        "api.main:app",
        host=config.api_host,
        port=config.api_port,
        reload=False,
    )