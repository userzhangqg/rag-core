#!/bin/bash

# RAG Core Services启动脚本
# 用于同时启动Gradio UI和FastAPI服务，并将日志输出到文件

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
API_PORT=8001
UI_PORT=7860
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
LOG_DIR="$PROJECT_ROOT/api/logs"
API_LOG_FILE="$LOG_DIR/api_server.log"
UI_LOG_FILE="$LOG_DIR/ui_server.log"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 帮助信息
usage() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -a, --api-port PORT    FastAPI服务端口 (默认: 8001)"
    echo "  -u, --ui-port PORT     Gradio UI端口 (默认: 7860)"
    echo "  -l, --log-dir DIR      日志目录 (默认: api/logs)"
    echo "  -r, --reload           启用自动重载模式"
    echo "  -h, --help             显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                    # 使用默认配置启动"
    echo "  $0 -a 9000 -u 7861    # 指定端口启动"
    echo "  $0 -r                 # 启用重载模式"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--api-port)
            API_PORT="$2"
            shift 2
            ;;
        -u|--ui-port)
            UI_PORT="$2"
            shift 2
            ;;
        -l|--log-dir)
            LOG_DIR="$2"
            shift 2
            ;;
        -r|--reload)
            RELOAD=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            usage
            exit 1
            ;;
    esac
done

# 更新日志文件路径
API_LOG_FILE="$LOG_DIR/api_server.log"
UI_LOG_FILE="$LOG_DIR/ui_server.log"
mkdir -p "$LOG_DIR"

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}错误: 端口 $port 已被占用${NC}"
        return 1
    fi
    return 0
}

# 检查端口
echo -e "${BLUE}检查端口可用性...${NC}"
if ! check_port $API_PORT || ! check_port $UI_PORT; then
    echo -e "${YELLOW}请使用其他端口或停止占用端口的进程${NC}"
    exit 1
fi

# 获取Python解释器路径
PYTHON_CMD="$(which python3)"
if [[ -z "$PYTHON_CMD" ]]; then
    PYTHON_CMD="$(which python)"
fi

if [[ -z "$PYTHON_CMD" ]]; then
    echo -e "${RED}错误: 未找到Python解释器${NC}"
    exit 1
fi

# 启动服务
echo -e "${GREEN}启动RAG Core服务...${NC}"
echo -e "${BLUE}项目根目录: $PROJECT_ROOT${NC}"
echo -e "${BLUE}Python解释器: $PYTHON_CMD${NC}"
echo -e "${BLUE}FastAPI端口: $API_PORT${NC}"
echo -e "${BLUE}Gradio UI端口: $UI_PORT${NC}"
echo -e "${BLUE}日志目录: $LOG_DIR${NC}"

# 启动FastAPI服务
echo -e "${YELLOW}启动FastAPI服务...${NC}"
cd "$PROJECT_ROOT"
if [[ "$RELOAD" == true ]]; then
    nohup $PYTHON_CMD -m uvicorn api.main:app --host 0.0.0.0 --port $API_PORT --reload > "$API_LOG_FILE" 2>&1 &
else
    nohup $PYTHON_CMD -m uvicorn api.main:app --host 0.0.0.0 --port $API_PORT > "$API_LOG_FILE" 2>&1 &
fi
API_PID=$!
echo "FastAPI服务PID: $API_PID"

# 等待FastAPI服务启动
echo -e "${YELLOW}等待FastAPI服务启动...${NC}"
sleep 3
if ! kill -0 $API_PID 2>/dev/null; then
    echo -e "${RED}FastAPI服务启动失败，请查看日志: $API_LOG_FILE${NC}"
    exit 1
fi

# 启动Gradio UI服务
echo -e "${YELLOW}启动Gradio UI服务...${NC}"
cd "$PROJECT_ROOT"
if [[ "$RELOAD" == true ]]; then
    nohup $PYTHON_CMD api/gradio_ui.py --with-api --api-port $API_PORT > "$UI_LOG_FILE" 2>&1 &
else
    nohup $PYTHON_CMD api/gradio_ui.py --with-api --api-port $API_PORT --no-reload > "$UI_LOG_FILE" 2>&1 &
fi
UI_PID=$!
echo "Gradio UI服务PID: $UI_PID"

# 等待Gradio UI服务启动
echo -e "${YELLOW}等待Gradio UI服务启动...${NC}"
sleep 3
if ! kill -0 $UI_PID 2>/dev/null; then
    echo -e "${RED}Gradio UI服务启动失败，请查看日志: $UI_LOG_FILE${NC}"
    echo -e "${YELLOW}停止FastAPI服务...${NC}"
    kill $API_PID 2>/dev/null
    exit 1
fi

# 显示服务信息
echo ""
echo -e "${GREEN}✅ 服务启动成功!${NC}"
echo -e "${GREEN}FastAPI服务: http://localhost:$API_PORT${NC}"
echo -e "${GREEN}Gradio UI: http://localhost:$UI_PORT${NC}"
echo -e "${GREEN}API日志: $API_LOG_FILE${NC}"
echo -e "${GREEN}UI日志: $UI_LOG_FILE${NC}"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"

# 保存PID到文件
echo $API_PID > "$LOG_DIR/api.pid"
echo $UI_PID > "$LOG_DIR/ui.pid"

# 捕获退出信号
cleanup() {
    echo -e "${YELLOW}正在停止服务...${NC}"
    if [[ -f "$LOG_DIR/api.pid" ]]; then
        API_PID=$(cat "$LOG_DIR/api.pid")
        if kill -0 $API_PID 2>/dev/null; then
            kill $API_PID
            echo -e "${GREEN}FastAPI服务已停止${NC}"
        fi
        rm -f "$LOG_DIR/api.pid"
    fi
    
    if [[ -f "$LOG_DIR/ui.pid" ]]; then
        UI_PID=$(cat "$LOG_DIR/ui.pid")
        if kill -0 $UI_PID 2>/dev/null; then
            kill $UI_PID
            echo -e "${GREEN}Gradio UI服务已停止${NC}"
        fi
        rm -f "$LOG_DIR/ui.pid"
    fi
    
    echo -e "${GREEN}所有服务已停止${NC}"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 实时监控日志
tail -f "$API_LOG_FILE" "$UI_LOG_FILE" 2>/dev/null &
TAIL_PID=$!

# 等待用户中断
wait $TAIL_PID