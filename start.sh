#!/bin/bash

# Z-Image 一键启动脚本
# 功能：打包前台并启动后台和前台服务

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_debug() {
    if [ "${DEBUG:-false}" = "true" ]; then
        echo -e "[DEBUG] $(date '+%Y-%m-%d %H:%M:%S') - $1"
    fi
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

log_info "开始启动 Z-Image 服务..."

# 检查必要工具
log_info "检查环境依赖..."
if ! command -v node &> /dev/null; then
    log_error "未找到 node，请先安装 Node.js"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    log_error "未找到 npm，请先安装 npm"
    exit 1
fi

if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    log_error "未找到 python，请先安装 Python"
    exit 1
fi

PYTHON_CMD="python"
if ! command -v python &> /dev/null; then
    PYTHON_CMD="python3"
fi

log_debug "使用 Python 命令: $PYTHON_CMD"
log_info "环境检查通过"

# 步骤1: 打包前台
log_info "开始打包前台应用..."
cd frontend

if [ ! -f "package.json" ]; then
    log_error "未找到 frontend/package.json，请检查项目结构"
    exit 1
fi

log_debug "执行: npm run build"
if npm run build; then
    log_info "前台打包完成"
else
    log_error "前台打包失败"
    exit 1
fi

cd ..

# 步骤2: 启动后台服务
log_info "启动后台服务..."
log_debug "执行: $PYTHON_CMD backend/app.py"

# 检查后台是否已在运行
PORT_5000_IN_USE=false
if command -v lsof &> /dev/null; then
    if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        PORT_5000_IN_USE=true
    fi
elif command -v netstat &> /dev/null; then
    if netstat -an 2>/dev/null | grep -q ":5000.*LISTEN"; then
        PORT_5000_IN_USE=true
    fi
fi

if [ "$PORT_5000_IN_USE" = true ]; then
    log_warn "端口 5000 已被占用，后台服务可能已在运行"
else
    # 后台运行 Flask 服务
    if command -v nohup &> /dev/null; then
        nohup $PYTHON_CMD backend/app.py > backend.log 2>&1 &
    else
        $PYTHON_CMD backend/app.py > backend.log 2>&1 &
    fi
    BACKEND_PID=$!
    log_info "后台服务已启动 (PID: $BACKEND_PID)"
    log_debug "后台服务日志: backend.log"
    
    # 等待一下确保服务启动
    sleep 2
    
    # 检查进程是否还在运行
    if command -v kill &> /dev/null; then
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            log_error "后台服务启动失败，请查看 backend.log"
            exit 1
        fi
    fi
fi

# 步骤3: 启动前台服务
log_info "启动前台服务..."
cd frontend
log_debug "执行: npm start"

# 检查前台是否已在运行
PORT_3000_IN_USE=false
if command -v lsof &> /dev/null; then
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        PORT_3000_IN_USE=true
    fi
elif command -v netstat &> /dev/null; then
    if netstat -an 2>/dev/null | grep -q ":3000.*LISTEN"; then
        PORT_3000_IN_USE=true
    fi
fi

if [ "$PORT_3000_IN_USE" = true ]; then
    log_warn "端口 3000 已被占用，前台服务可能已在运行"
else
    # 后台运行 Next.js 服务
    if command -v nohup &> /dev/null; then
        nohup npm start > ../frontend.log 2>&1 &
    else
        npm start > ../frontend.log 2>&1 &
    fi
    FRONTEND_PID=$!
    log_info "前台服务已启动 (PID: $FRONTEND_PID)"
    log_debug "前台服务日志: frontend.log"
    
    # 等待一下确保服务启动
    sleep 2
    
    # 检查进程是否还在运行
    if command -v kill &> /dev/null; then
        if ! kill -0 $FRONTEND_PID 2>/dev/null; then
            log_error "前台服务启动失败，请查看 frontend.log"
            exit 1
        fi
    fi
fi

cd ..

# 完成
log_info "========================================="
log_info "服务启动完成！"
log_info "========================================="
log_info "后台服务: http://localhost:5000"
log_info "前台服务: http://localhost:3000"
log_info ""
log_info "查看日志:"
log_info "  后台日志: tail -f backend.log"
log_info "  前台日志: tail -f frontend.log"
log_info ""
log_info "停止服务:"
if [ -n "$BACKEND_PID" ]; then
    log_info "  后台: kill $BACKEND_PID"
fi
if [ -n "$FRONTEND_PID" ]; then
    log_info "  前台: kill $FRONTEND_PID"
fi
log_info "========================================="

