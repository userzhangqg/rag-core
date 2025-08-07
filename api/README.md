# RAG Core 服务启动脚本

## 简介

`start_services.sh` 是一个用于同时启动 FastAPI 和 Gradio UI 服务的 shell 脚本，支持日志管理和进程控制。

## 使用方法

### 基本使用
```bash
./start_services.sh
```

### 自定义端口
```bash
./start_services.sh -a 9000 -u 7861
```

### 启用重载模式（开发环境）
```bash
./start_services.sh -r
```

### 自定义日志目录
```bash
./start_services.sh -l /path/to/logs
```

## 命令行参数

| 参数 | 长参数 | 说明 | 默认值 |
|------|--------|------|--------|
| -a | --api-port | FastAPI服务端口 | 8000 |
| -u | --ui-port | Gradio UI端口 | 7860 |
| -l | --log-dir | 日志目录 | api/logs |
| -r | --reload | 启用自动重载模式 | 禁用 |
| -h | --help | 显示帮助信息 | - |

## 日志文件

脚本会在指定的日志目录下创建以下文件：
- `api_server.log` - FastAPI服务的输出日志
- `ui_server.log` - Gradio UI服务的输出日志
- `api.pid` - FastAPI服务的进程ID
- `ui.pid` - Gradio UI服务的进程ID

## 访问地址

- FastAPI文档: http://localhost:8000/docs
- Gradio UI界面: http://localhost:7860

## 停止服务

按 `Ctrl+C` 可以优雅地停止所有服务，脚本会自动清理PID文件和停止相关进程。