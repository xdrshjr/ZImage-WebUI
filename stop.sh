#!/bin/bash

# Z-Image 一键停止脚本
# 功能：停止后台和前台服务

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

log_info "开始停止 Z-Image 服务..."

# 停止后台服务（端口 5000）
log_info "停止后台服务（端口 5000）..."
BACKEND_STOPPED=false

# 方法1: 使用 lsof 查找进程
if command -v lsof &> /dev/null; then
    BACKEND_PIDS=$(lsof -ti :5000 2>/dev/null)
    if [ -n "$BACKEND_PIDS" ]; then
        for PID in $BACKEND_PIDS; do
            log_debug "找到后台进程 PID: $PID"
            if kill $PID 2>/dev/null; then
                log_info "已停止后台进程 (PID: $PID)"
                BACKEND_STOPPED=true
            else
                log_warn "无法停止后台进程 (PID: $PID)，可能已停止"
            fi
        done
    fi
fi

# 方法2: 使用 netstat 查找进程（如果 lsof 不可用或未找到）
if [ "$BACKEND_STOPPED" = false ] && command -v netstat &> /dev/null && command -v awk &> /dev/null && command -v grep &> /dev/null; then
    # Linux 系统
    if netstat -tlnp 2>/dev/null | grep -q ":5000.*LISTEN"; then
        BACKEND_PIDS=$(netstat -tlnp 2>/dev/null | grep ":5000.*LISTEN" | awk '{print $7}' | cut -d'/' -f1 | sort -u)
        for PID in $BACKEND_PIDS; do
            if [ -n "$PID" ] && [ "$PID" != "-" ]; then
                log_debug "找到后台进程 PID: $PID"
                if kill $PID 2>/dev/null; then
                    log_info "已停止后台进程 (PID: $PID)"
                    BACKEND_STOPPED=true
                fi
            fi
        done
    fi
fi

# 方法3: 通过进程名查找 Python app.py 进程
if [ "$BACKEND_STOPPED" = false ] && command -v ps &> /dev/null && command -v grep &> /dev/null; then
    BACKEND_PIDS=$(ps aux | grep "[p]ython.*app.py" | awk '{print $2}' 2>/dev/null)
    if [ -n "$BACKEND_PIDS" ]; then
        for PID in $BACKEND_PIDS; do
            log_debug "通过进程名找到后台进程 PID: $PID"
            if kill $PID 2>/dev/null; then
                log_info "已停止后台进程 (PID: $PID)"
                BACKEND_STOPPED=true
            fi
        done
    fi
fi

if [ "$BACKEND_STOPPED" = false ]; then
    log_warn "未找到运行中的后台服务"
fi

# 等待进程完全停止
if [ "$BACKEND_STOPPED" = true ]; then
    sleep 1
    # 检查是否还有进程在运行
    REMAINING_PIDS=$(lsof -ti :5000 2>/dev/null || echo "")
    if [ -n "$REMAINING_PIDS" ]; then
        log_warn "仍有进程占用端口 5000，尝试强制停止..."
        for PID in $REMAINING_PIDS; do
            kill -9 $PID 2>/dev/null && log_info "强制停止后台进程 (PID: $PID)" || true
        done
    fi
fi

# 停止前台服务（端口 3000）
log_info "停止前台服务（端口 3000）..."
FRONTEND_STOPPED=false

# 方法1: 使用 lsof 查找进程
if command -v lsof &> /dev/null; then
    FRONTEND_PIDS=$(lsof -ti :3000 2>/dev/null)
    if [ -n "$FRONTEND_PIDS" ]; then
        for PID in $FRONTEND_PIDS; do
            log_debug "找到前台进程 PID: $PID"
            if kill $PID 2>/dev/null; then
                log_info "已停止前台进程 (PID: $PID)"
                FRONTEND_STOPPED=true
            else
                log_warn "无法停止前台进程 (PID: $PID)，可能已停止"
            fi
        done
    fi
fi

# 方法2: 使用 netstat 查找进程（如果 lsof 不可用或未找到）
if [ "$FRONTEND_STOPPED" = false ] && command -v netstat &> /dev/null && command -v awk &> /dev/null && command -v grep &> /dev/null; then
    # Linux 系统
    if netstat -tlnp 2>/dev/null | grep -q ":3000.*LISTEN"; then
        FRONTEND_PIDS=$(netstat -tlnp 2>/dev/null | grep ":3000.*LISTEN" | awk '{print $7}' | cut -d'/' -f1 | sort -u)
        for PID in $FRONTEND_PIDS; do
            if [ -n "$PID" ] && [ "$PID" != "-" ]; then
                log_debug "找到前台进程 PID: $PID"
                if kill $PID 2>/dev/null; then
                    log_info "已停止前台进程 (PID: $PID)"
                    FRONTEND_STOPPED=true
                fi
            fi
        done
    fi
fi

# 方法3: 通过进程名查找 Node.js next 进程
if [ "$FRONTEND_STOPPED" = false ] && command -v ps &> /dev/null && command -v grep &> /dev/null && command -v awk &> /dev/null; then
    # 查找 next start 相关的 Node 进程
    FRONTEND_PIDS=$(ps aux | grep -E "[n]ode.*next|[n]pm.*start" | awk '{print $2}' 2>/dev/null)
    if [ -n "$FRONTEND_PIDS" ]; then
        for PID in $FRONTEND_PIDS; do
            log_debug "通过进程名找到前台进程 PID: $PID"
            if kill $PID 2>/dev/null; then
                log_info "已停止前台进程 (PID: $PID)"
                FRONTEND_STOPPED=true
            fi
        done
    fi
fi

if [ "$FRONTEND_STOPPED" = false ]; then
    log_warn "未找到运行中的前台服务"
fi

# 等待进程完全停止
if [ "$FRONTEND_STOPPED" = true ]; then
    sleep 1
    # 检查是否还有进程在运行
    REMAINING_PIDS=$(lsof -ti :3000 2>/dev/null || echo "")
    if [ -n "$REMAINING_PIDS" ]; then
        log_warn "仍有进程占用端口 3000，尝试强制停止..."
        for PID in $REMAINING_PIDS; do
            kill -9 $PID 2>/dev/null && log_info "强制停止前台进程 (PID: $PID)" || true
        done
    fi
fi

# 完成
log_info "========================================="
if [ "$BACKEND_STOPPED" = true ] || [ "$FRONTEND_STOPPED" = true ]; then
    log_info "服务停止完成！"
else
    log_info "未发现运行中的服务"
fi
log_info "========================================="

