#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG Core API Main Entry
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import configuration
from conf.config import RAGConfig

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
# TODO: Include routers for different modules
# app.include_router(documents.router, prefix="/documents", tags=["documents"])


@app.get("/")
async def root():
    """Root endpoint for the API."""
    return {"message": "Welcome to the RAG Core API"}


@app.get("/health")
async def health_check():
    """Health check endpoint for the API."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    # Get default configuration
    config = RAGConfig.from_config_file()
    uvicorn.run(
        "main:app",
        host=config.api_host,
        port=config.api_port,
        reload=True
    )