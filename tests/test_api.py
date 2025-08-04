#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG Core API 测试
"""

import pytest
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient

# 设置测试环境变量
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# 导入应用
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

client = TestClient(app)


class TestRAGAPI:
    """RAG API测试类"""
    
    def test_health_check(self):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "endpoints" in data
    
    def test_root_endpoint(self):
        """测试根端点"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
    
    def test_upload_text(self):
        """测试文本上传"""
        test_content = "这是一个测试文档内容，用于测试API功能。"
        response = client.post(
            "/documents/upload-text",
            json={
                "content": test_content,
                "source_name": "test_document"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["chunks_count"] > 0
    
    def test_chat_query(self):
        """测试对话查询"""
        # 先上传一些测试内容
        test_content = "Python是一种编程语言，具有简洁、易读的特点。"
        client.post(
            "/documents/upload-text",
            json={
                "content": test_content,
                "source_name": "test_python"
            }
        )
        
        # 执行查询
        response = client.post(
            "/chat/query",
            json={
                "query": "Python有什么特点？",
                "top_k": 3
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["status"] == "success"
    
    def test_invalid_chat_query(self):
        """测试无效查询"""
        response = client.post(
            "/chat/query",
            json={"query": ""}
        )
        assert response.status_code == 400
    
    def test_documents_health(self):
        """测试文档系统健康检查"""
        response = client.get("/documents/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_chat_health(self):
        """测试对话系统健康检查"""
        response = client.get("/chat/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


def test_file_upload():
    """测试文件上传功能"""
    # 创建临时测试文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
        tmp_file.write("这是一个测试文件内容，用于测试文件上传功能。")
        tmp_file.flush()
        
        try:
            # 测试文件上传
            with open(tmp_file.name, 'rb') as f:
                response = client.post(
                    "/documents/upload",
                    files={"file": ("test.txt", f, "text/plain")}
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["chunks_count"] > 0
            
        finally:
            # 清理临时文件
            os.unlink(tmp_file.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])