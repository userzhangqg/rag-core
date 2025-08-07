# MinerU VLM PDF解析器使用指南

## 概述

本解析器基于MinerU项目的VLM后端实现，支持通过URL调用远程VLM服务进行PDF解析。相比传统的pipeline解析，VLM后端提供了更强大的文档理解能力。

## 主要特性

- **VLM后端支持**: 支持`sglang-client`、`transformers`、`sglang-engine`等多种后端
- **URL调用**: 可通过HTTP URL调用远程VLM服务
- **异步处理**: 支持异步批量处理PDF文件
- **多种输出格式**: 支持Markdown、JSON内容列表、中间格式等
- **灵活配置**: 支持公式解析、表格解析、语言选择等

## 安装依赖

确保已安装MinerU及其依赖：

```bash
pip install mineru
# 或从源码安装
pip install -e /path/to/MinerU
```

## 快速开始

### 1. 基本使用

```python
from rag_core.core.parser.pdf_mineru_parser import MineruVLMParser

# 初始化解析器（使用VLM后端和远程服务）
parser = MineruVLMParser(
    backend="sglang-client",  # 使用sglang客户端
    server_url="http://localhost:8000",  # VLM服务器地址
    lang=["ch", "en"],  # 支持中英文
    formula_enable=True,  # 启用公式解析
    table_enable=True     # 启用表格解析
)

# 处理单个PDF
result = parser.process_single_pdf(
    pdf_path="/path/to/document.pdf",
    output_dir="./output/document"
)

print(f"处理状态: {result['status']}")
print(f"输出目录: {result['output_dir']}")
```

### 2. 批量处理

```python
# 批量处理PDF文件
result = parser.process_batch_pdfs(
    pdfs_dir="/path/to/pdfs",
    output_base_dir="./output",
    skip_existing=True  # 跳过已处理的文件
)

print(f"总文件数: {result['total_pdfs']}")
print(f"成功处理: {result['processed_pdfs']}")
print(f"失败: {result['failed_pdfs']}")
```

### 3. 异步处理

```python
import asyncio

# 异步批量处理
async def batch_process():
    result = await parser.aprocess_batch_pdfs(
        pdfs_dir="/path/to/pdfs",
        output_base_dir="./output"
    )
    return result

# 运行异步任务
result = asyncio.run(batch_process())
```

### 4. 快速获取内容

```python
# 快速获取PDF的markdown内容（不保存文件）
markdown_content = parser.get_markdown_content("/path/to/document.pdf")
if markdown_content:
    print(markdown_content[:500] + "...")  # 打印前500字符
```

## 后端类型说明

| 后端类型 | 描述 | 必需参数 |
|---------|------|----------|
| `sglang-client` | 通过URL调用sglang服务 | `server_url` |
| `transformers` | 本地transformers模型 | `model_path` |
| `sglang-engine` | 本地sglang引擎 | `model_path` |
| `pipeline` | 传统pipeline解析 | 无 |

## VLM服务器配置

### 使用Docker启动VLM服务

```bash
# 启动sglang服务
docker run -itd --name=mineru_server --gpus=all -p 8888:8000 quincyqiang/mineru:0.2-models

# 服务启动后，访问地址为：http://localhost:8888/docs
```

### 使用本地服务

```bash
# 启动本地sglang服务
python -m sglang.launch_server --model-path your-model-path --port 30000
```

## 命令行使用

```bash
# 处理单个PDF
python pdf_mineru_parser.py --pdf /path/to/document.pdf --output ./output

# 批量处理PDF目录
python pdf_mineru_parser.py --dir /path/to/pdfs --output ./output

# 使用特定后端和服务器
python pdf_mineru_parser.py --pdf /path/to/document.pdf \
    --backend sglang-client \
    --server-url http://localhost:8888 \
    --output ./output

# 异步批量处理
python pdf_mineru_parser.py --dir /path/to/pdfs --output ./output --async
```

## 输出文件说明

处理完成后，每个PDF会生成以下文件：

- `content.md`: 主要的Markdown格式内容
- `content_list.json`: 结构化的内容列表（JSON格式）
- `middle.json`: 中间处理结果（JSON格式）
- `images/`: 提取的图片目录

## 错误处理

```python
result = parser.process_single_pdf("/path/to/document.pdf", "./output")

if result["status"] == "error":
    print(f"处理失败: {result['error']}")
else:
    print("处理成功")
    print(f"文件: {result['pdf_filename']}")
    print(f"语言: {result['used_language']}")
```

## 配置示例

### 中文文档处理

```python
parser = MineruVLMParser(
    backend="sglang-client",
    server_url="http://localhost:8888",
    lang=["ch"],
    formula_enable=True,
    table_enable=True
)
```

### 英文文档处理

```python
parser = MineruVLMParser(
    backend="sglang-client",
    server_url="http://localhost:8888",
    lang=["en"],
    formula_enable=False,  # 英文文档通常公式较少
    table_enable=True
)
```

### 本地模型处理

```python
parser = MineruVLMParser(
    backend="transformers",
    model_path="/path/to/local/model",
    lang=["ch", "en"],
    formula_enable=True,
    table_enable=True
)
```

## 注意事项

1. **服务器连接**: 确保VLM服务器已启动并可访问
2. **资源消耗**: VLM解析可能消耗较多GPU资源
3. **网络延迟**: 远程URL调用可能受网络影响
4. **文件大小**: 大文件处理可能需要较长时间
5. **语言支持**: 根据文档语言选择合适的语言配置

## 故障排除

### 连接失败

```python
# 检查服务器状态
import requests
try:
    response = requests.get("http://localhost:8888/health")
    print("服务器状态:", response.status_code)
except Exception as e:
    print("连接失败:", e)
```

### 内存不足

- 减少并发处理数量
- 使用较小的批处理大小
- 考虑使用CPU模式（如果可用）

### 超时问题

```python
# 增加超时时间
parser = MineruVLMParser(
    backend="sglang-client",
    server_url="http://localhost:8888",
    timeout=300  # 5分钟超时
)
```

## 性能优化建议

1. **批量处理**: 使用批量处理减少单次调用开销
2. **异步处理**: 使用异步API提高并发处理能力
3. **缓存**: 对重复文件使用缓存避免重复处理
4. **资源监控**: 监控GPU和内存使用情况
5. **负载均衡**: 使用多个VLM服务器分担负载