# Gradio Web UI for RAG Core

这是一个基于Gradio的Web界面，为RAG Core系统提供用户友好的文档上传和知识库问答功能。

## 功能特性

### 📁 文档上传
- 支持多种文件格式：PDF、TXT、MD、DOCX、HTML
- 拖拽上传或选择文件
- 支持直接粘贴文本内容
- 可指定目标集合（collection）

### ❓ 知识库问答
- 智能问答基于上传的文档内容
- 可调节返回结果数量（Top K）
- 支持结果重排序（Re-ranking）
- 显示答案来源和置信度

### 🎯 用户界面
- 响应式设计，支持移动端
- 实时状态反馈
- 直观的标签页导航
- 详细的使用说明

## 安装和运行

### 1. 安装依赖

首先确保已安装所有依赖：

```bash
pip install -r requirements.txt
```

### 2. 启动Gradio Web UI

#### 方法1：直接运行
```bash
python gradio_ui.py
```

#### 方法2：指定端口运行
```bash
python gradio_ui.py --server_port 7860
```

### 3. 访问Web界面

启动后，打开浏览器访问：
- 本地访问：http://localhost:7860
- 局域网访问：http://[你的IP]:7860

## 使用步骤

### 1. 准备知识库
1. 打开"📁 Document Upload"标签页
2. 选择以下任一方式添加内容：
   - **上传文件**：点击或拖拽文件到上传区域
   - **添加文本**：在文本框中粘贴内容
3. 选择目标集合（默认使用"default"）
4. 点击对应按钮处理内容

### 2. 开始问答
1. 切换到"❓ Knowledge Q&A"标签页
2. 在输入框中输入你的问题
3. 选择对应的集合
4. 调整参数：
   - **Top K Results**：返回相关文档数量（1-20）
   - **Use Re-ranking**：是否使用重排序提升准确性
5. 点击"🔍 Ask Question"获取答案

### 3. 查看结果
- 答案会以Markdown格式显示
- 包含答案文本和相关文档来源
- 显示每个来源的置信度分数

## 界面截图

### 文档上传界面
![Document Upload](docs/images/gradio_upload.png)

### 问答界面
![Q&A Interface](docs/images/gradio_qa.png)

## 高级用法

### 自定义配置
可以通过修改配置文件来自定义Gradio界面：

```python
# 在gradio_ui.py中修改以下参数
interface.launch(
    server_name="0.0.0.0",  # 监听地址
    server_port=7860,       # 端口号
    share=False,            # 是否创建公开链接
    debug=True              # 调试模式
)
```

### 集成到现有系统
Gradio界面可以集成到现有的FastAPI应用中：

```python
from gradio_ui import create_gradio_interface
import gradio as gr

# 创建Gradio应用
app = create_gradio_interface()

# 作为FastAPI的子应用
from fastapi import FastAPI
fastapi_app = FastAPI()
gr.mount_gradio_app(fastapi_app, app, path="/gradio")
```

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查看端口占用
   lsof -i :7860
   # 使用其他端口
   python gradio_ui.py --server_port 7861
   ```

2. **依赖问题**
   ```bash
   # 更新gradio
   pip install --upgrade gradio
   ```

3. **权限问题**
   ```bash
   # 确保有读取文件的权限
   chmod +x gradio_ui.py
   ```

### 日志查看
Gradio应用的日志会显示在终端中，包括：
- 文件处理状态
- 查询结果
- 错误信息

## API集成

Gradio界面与现有的RAG Core API完全兼容，共享相同的：
- 配置文件（conf/config.yaml）
- 向量数据库（Weaviate）
- 处理管道（RAGPipeline）

## 开发说明

### 代码结构
```
gradio_ui.py          # 主要的Gradio界面文件
├── GradioRAGInterface # 核心功能类
│   ├── process_uploaded_file()  # 处理文件上传
│   ├── process_text_content()   # 处理文本内容
│   ├── query_knowledge_base()   # 知识库查询
│   └── list_collections()       # 列出集合
└── create_gradio_interface()    # 创建界面
```

### 扩展开发
要添加新功能，可以：
1. 在GradioRAGInterface类中添加新方法
2. 在create_gradio_interface()中添加新组件
3. 更新事件处理器

## 性能优化

### 大文件处理
- 对于大文件，建议分批处理
- 使用SSD存储提升处理速度
- 调整chunk_size参数优化内存使用

### 查询优化
- 合理设置Top K值（5-10通常足够）
- 启用重排序提升准确性
- 使用合适的embedding模型

## 安全考虑

- 默认监听0.0.0.0，如需限制访问可改为127.0.0.1
- 文件上传有大小限制，可在配置中调整
- 建议在生产环境中使用反向代理（nginx）