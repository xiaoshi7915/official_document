#!/bin/bash

# 官方AI写作系统 - 系统监控脚本
# 用于监控系统状态、查看日志、重启服务等

PROJECT_DIR="/opt/official_ai_writer/official_document"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_status() {
    local status=$1
    local message=$2
    case $status in
        "success")
            echo -e "${GREEN}✓ $message${NC}"
            ;;
        "error")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "warning")
            echo -e "${YELLOW}⚠ $message${NC}"
            ;;
        "info")
            echo -e "${BLUE}ℹ $message${NC}"
            ;;
    esac
}

# 检查服务状态
check_services() {
    echo "=== 系统服务状态检查 ==="
    echo ""
    
    # 检查后端服务
    if ps aux | grep "python.*main.py" | grep -v grep | grep -q "main.py"; then
        BACKEND_PID=$(ps aux | grep "python.*main.py" | grep -v grep | grep "main.py" | awk '{print $2}' | head -1)
        print_status "success" "后端服务正在运行 (PID: $BACKEND_PID)"
    else
        print_status "error" "后端服务未运行"
    fi
    
    # 检查前端服务
    if ps aux | grep "前端服务器.py" | grep -v grep | grep -q "前端服务器.py"; then
        FRONTEND_PID=$(ps aux | grep "前端服务器.py" | grep -v grep | awk '{print $2}' | head -1)
        print_status "success" "前端服务正在运行 (PID: $FRONTEND_PID)"
    else
        print_status "error" "前端服务未运行"
    fi
    
    echo ""
}

# 检查端口状态
check_ports() {
    echo "=== 端口状态检查 ==="
    echo ""
    
    # 检查后端端口
    if netstat -tlnp 2>/dev/null | grep -q ":5003"; then
        print_status "success" "后端端口 5003 正在监听"
    else
        print_status "error" "后端端口 5003 未监听"
    fi
    
    # 检查前端端口
    if netstat -tlnp 2>/dev/null | grep -q ":8081"; then
        print_status "success" "前端端口 8081 正在监听"
    else
        print_status "error" "前端端口 8081 未监听"
    fi
    
    echo ""
}

# 测试API接口
test_apis() {
    echo "=== API接口测试 ==="
    echo ""
    
    # 测试后端API
    if curl -s http://localhost:5003/api/templates > /dev/null; then
        print_status "success" "后端API正常"
    else
        print_status "error" "后端API异常"
    fi
    
    # 测试前端API代理
    if curl -s http://localhost:8081/api/templates > /dev/null; then
        print_status "success" "前端API代理正常"
    else
        print_status "error" "前端API代理异常"
    fi
    
    # 测试前端页面
    if curl -s http://localhost:8081 | grep -q "党政机关公文生成智能体"; then
        print_status "success" "前端页面正常"
    else
        print_status "error" "前端页面异常"
    fi
    
    echo ""
}

# 查看日志
view_logs() {
    echo "=== 日志查看 ==="
    echo ""
    echo "1. 查看后端日志"
    echo "2. 查看前端日志"
    echo "3. 查看系统日志"
    echo "4. 返回主菜单"
    echo ""
    read -p "请选择 (1-4): " log_choice
    
    case $log_choice in
        1)
            echo "=== 后端日志 (最近50行) ==="
            if [ -f "$BACKEND_DIR/backend.log" ]; then
                tail -50 "$BACKEND_DIR/backend.log"
            else
                print_status "error" "后端日志文件不存在"
            fi
            ;;
        2)
            echo "=== 前端日志 (最近50行) ==="
            if [ -f "$PROJECT_DIR/frontend.log" ]; then
                tail -50 "$PROJECT_DIR/frontend.log"
            else
                print_status "error" "前端日志文件不存在"
            fi
            ;;
        3)
            echo "=== 系统日志 (最近20行) ==="
            journalctl -u official-ai-writer --no-pager -n 20 2>/dev/null || echo "无法获取系统日志"
            ;;
        4)
            return
            ;;
        *)
            print_status "error" "无效选择"
            ;;
    esac
    
    echo ""
    read -p "按回车键继续..."
}

# 重启服务
restart_services() {
    echo "=== 重启服务 ==="
    echo ""
    
    print_status "info" "正在停止现有服务..."
    pkill -f "python.*main.py" 2>/dev/null
    pkill -f "前端服务器.py" 2>/dev/null
    sleep 3
    
    print_status "info" "正在启动后端服务..."
    cd "$BACKEND_DIR"
    source venv/bin/activate
    nohup python main.py > backend.log 2>&1 &
    echo $! > backend.pid
    
    print_status "info" "正在启动前端服务..."
    cd "$PROJECT_DIR"
    nohup python 前端服务器.py > frontend.log 2>&1 &
    echo $! > frontend.pid
    
    sleep 5
    
    print_status "success" "服务重启完成"
    echo ""
}

# 系统信息
system_info() {
    echo "=== 系统信息 ==="
    echo ""
    
    echo "系统时间: $(date)"
    echo "系统负载: $(uptime | awk -F'load average:' '{print $2}')"
    echo "内存使用: $(free -h | grep Mem | awk '{print $3"/"$2}')"
    echo "磁盘使用: $(df -h / | tail -1 | awk '{print $5}')"
    echo ""
    
    echo "项目目录: $PROJECT_DIR"
    echo "后端目录: $BACKEND_DIR"
    echo "前端目录: $FRONTEND_DIR"
    echo ""
    
    # Python版本
    if [ -f "$BACKEND_DIR/venv/bin/python" ]; then
        echo "Python版本: $($BACKEND_DIR/venv/bin/python --version)"
    fi
    
    # Node.js版本
    if command -v node &> /dev/null; then
        echo "Node.js版本: $(node --version)"
    fi
    
    echo ""
}

# 快速修复
quick_fix() {
    echo "=== 快速修复 ==="
    echo ""
    
    print_status "info" "执行快速修复流程..."
    
    # 1. 重新构建前端
    print_status "info" "重新构建前端..."
    cd "$FRONTEND_DIR"
    npm run build
    
    # 2. 复制模板文件
    print_status "info" "复制模板文件..."
    cd "$PROJECT_DIR"
    cp -r frontend/public/templates frontend/dist/ 2>/dev/null
    cp -r frontend/templates frontend/dist/ 2>/dev/null
    
    # 3. 重启服务
    print_status "info" "重启服务..."
    restart_services
    
    print_status "success" "快速修复完成"
    echo ""
}

# 主菜单
show_menu() {
    clear
    echo "=========================================="
    echo "    官方AI写作系统 - 系统监控工具"
    echo "=========================================="
    echo ""
    echo "1. 检查服务状态"
    echo "2. 检查端口状态"
    echo "3. 测试API接口"
    echo "4. 查看日志"
    echo "5. 重启服务"
    echo "6. 系统信息"
    echo "7. 快速修复"
    echo "8. 访问系统"
    echo "9. 退出"
    echo ""
}

# 主程序
main() {
    while true; do
        show_menu
        read -p "请选择操作 (1-9): " choice
        
        case $choice in
            1)
                check_services
                read -p "按回车键继续..."
                ;;
            2)
                check_ports
                read -p "按回车键继续..."
                ;;
            3)
                test_apis
                read -p "按回车键继续..."
                ;;
            4)
                view_logs
                ;;
            5)
                restart_services
                read -p "按回车键继续..."
                ;;
            6)
                system_info
                read -p "按回车键继续..."
                ;;
            7)
                quick_fix
                read -p "按回车键继续..."
                ;;
            8)
                echo ""
                print_status "info" "系统访问地址:"
                echo "前端界面: http://localhost:8081"
                echo "后端API: http://localhost:5003"
                echo ""
                read -p "按回车键继续..."
                ;;
            9)
                print_status "info" "退出监控工具"
                exit 0
                ;;
            *)
                print_status "error" "无效选择，请重新输入"
                sleep 2
                ;;
        esac
    done
}

# 如果直接运行脚本，显示完整状态
if [ "$1" = "status" ]; then
    check_services
    check_ports
    test_apis
    system_info
    exit 0
fi

# 启动主程序
main 