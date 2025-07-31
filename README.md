# RAG Core System

RAG Core是一个核心RAG（Retrieval-Augmented Generation）知识库系统，支持文档上传、解析、分片、向量化、用户检索、召回、重排、Prompt处理和LLM生成等功能。系统提供API和命令行两种交互方式。

## 技术栈

- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker
- Langchain
- LlamaIndex
- MinIO
- Weaviate
- Redis

## 项目结构

```
rag-core/
├── api/              # API接口实现
├── core/             # 核心模块
│   ├── chunking/     # 文档分片模块
│   ├── llm/          # 大语言模型模块
│   ├── parser/       # 文档解析模块
│   ├── pipeline/     # 处理流程模块
│   ├── reranker/     # 重排模块
│   ├── retrieval/    # 检索模块
│   └── vector/       # 向量化模块
├── data/             # 测试数据
├── docs/             # 文档
├── examples/         # 使用示例
├── tests/            # 测试代码
├── main.py           # 程序入口
├── cli.py            # 命令行接口
├── config.py         # 配置文件
├── requirements.txt  # 依赖列表
├── Dockerfile        # Docker配置
└── docker-compose.yml # Docker Compose配置
```

## 快速开始

### 使用Docker运行

```bash
# 克隆项目
git clone <repository-url>

# 进入项目目录
cd rag-core

# 启动所有服务
docker-compose up -d
```

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 下载NLTK数据
python download_nltk_data.py

# 运行API服务
python main.py
```

### 配置

系统配置存储在 `config.yaml` 文件中。您可以修改此文件来更改数据库连接、API端口等设置。

您也可以通过设置 `RAG_CORE_CONFIG` 环境变量来指定不同的配置文件路径。

#### Embedding配置

系统支持多种Embedding提供商，包括本地API和硅基流动。您可以在配置文件中指定使用的提供商及相应参数：

```yaml
embedding:
  provider: "local_api"  # 可选: "local_api", "siliconflow"
  local_api:
    url: "http://172.16.89.10:10669/scbllm/embedding-infer/embedding"
  siliconflow:
    api_key: "your-siliconflow-api-key-here"
    model_name: "BAAI/bge-large-zh-v1.5"
    api_url: "https://api.siliconflow.cn/v1/embeddings"
```

#### 向量数据库配置

系统使用Weaviate作为向量数据库。您可以在配置文件中指定Weaviate服务器的URL：

```yaml
vector_db:
  url: "http://localhost:8080"
```

#### 日志配置

系统使用Loguru作为日志库，支持同时输出到控制台和文件。您可以在配置文件中指定日志级别、格式和文件路径：

```yaml
logging:
  level: INFO
  console_level: INFO
  file_level: DEBUG
  file: logs/rag_core.log
  max_file_size: 10485760  # 10MB
  backup_count: 5
  format: "{time:YYYY-MM-DD HH:mm:ss} [{level}] [{name}] {message}"
  date_format: "%Y-%m-%d %H:%M:%S"
```

## 开发指南

请参考 [docs/dev_plan.md](docs/dev_plan.md) 了解详细的开发计划。

## 许可证

[MIT License](LICENSE)