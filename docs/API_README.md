# RAG Core API 使用指南

## 概述

RAG Core API 提供了一个完整的RESTful接口，用于文档上传、处理和基于RAG的对话功能。

## 快速开始

### 启动API服务

```bash
cd /rag-core
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### 使用Docker启动

```bash
docker-compose up --build
```

## API端点

### 基础端点

- **GET /** - API信息
- **GET /health** - 健康检查

### 文档管理

#### 文件上传
- **POST /documents/upload**
  - 上传文件并向量化
  - 支持格式：.md, .txt, .pdf, .docx, .html
  - 请求格式：multipart/form-data
  - 示例：
    ```bash
    curl -X POST "http://localhost:8000/documents/upload" \
         -F "file=@example.md"
    ```

#### 文本上传
- **POST /documents/upload-text**
  - 上传文本内容并向量化
  - 请求格式：JSON
  - 示例：
    ```bash
    curl -X POST "http://localhost:8000/documents/upload-text" \
         -H "Content-Type: application/json" \
         -d '{"content": "这是要上传的文本内容", "source_name": "example"}'
    ```

#### 健康检查
- **GET /documents/health**
  - 检查文档处理系统状态

### 对话功能

#### 标准查询
- **POST /chat/query**
  - 基于RAG的对话查询
  - 请求格式：JSON
  - 示例：
    ```bash
    curl -X POST "http://localhost:8000/chat/query" \
         -H "Content-Type: application/json" \
         -d '{"query": "Python有什么特点？", "top_k": 5}'
    ```

#### 流式查询
- **POST /chat/query-stream**
  - 流式响应的对话查询
  - 返回Server-Sent Events (SSE)
  - 示例：
    ```bash
    curl -X POST "http://localhost:8000/chat/query-stream" \
         -H "Content-Type: application/json" \
         -d '{"query": "Python有什么特点？", "stream": true}'
    ```

#### 健康检查
- **GET /chat/health**
  - 检查对话系统状态

## 数据模型

### 请求模型

#### ChatRequest
```json
{
  "query": "string",
  "top_k": 5,
  "score_threshold": 0.0,
  "use_rerank": true,
  "stream": false
}
```

#### TextUploadRequest
```json
{
  "content": "string",
  "source_name": "string"
}
```

### 响应模型

#### FileUploadResponse
```json
{
  "filename": "string",
  "chunks_count": 0,
  "status": "success",
  "message": "string"
}
```

#### ChatResponse
```json
{
  "response": "string",
  "status": "success"
}
```

## 使用示例

### Python示例

```python
import requests

# 上传文档
with open('example.md', 'rb') as f:
    response = requests.post('http://localhost:8000/documents/upload', files={'file': f})
    print(response.json())

# 对话查询
response = requests.post('http://localhost:8000/chat/query', json={
    'query': 'Python有什么特点？',
    'top_k': 5
})
print(response.json()['response'])
```

### 完整示例

参考 `examples/api_usage_example.py` 文件获取更多使用示例。

## 测试

运行测试：
```bash
python -m pytest tests/test_api.py -v
```

## 配置

API使用与CLI相同的配置文件 `conf/config.yaml`。可以通过环境变量或配置文件自定义：

- 向量数据库配置
- LLM服务配置
- 嵌入模型配置
- 重排序器配置

## 错误处理

API返回标准的HTTP状态码：
- 200: 成功
- 400: 请求错误
- 500: 服务器错误
- 503: 服务不可用

所有错误响应都包含详细的错误信息。