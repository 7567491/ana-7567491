#!/bin/bash
# 6页网用户活动日报启动脚本 - 生产级配置

# 设置脚本目录
SCRIPT_DIR="/www/wwwroot/ana"
WEBHOOK_SCRIPT="$SCRIPT_DIR/webhook.py"
LOG_DIR="$SCRIPT_DIR/logs"
PID_FILE="$SCRIPT_DIR/webhook.pid"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "错误: Python3 未安装"
        exit 1
    fi
    
    echo "使用Python版本: $(python3 --version)"
}

# 检查依赖
check_dependencies() {
    echo "检查依赖包..."
    python3 -c "import pymysql, requests, json" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "错误: 缺少必要依赖包"
        echo "请运行: pip3 install pymysql requests"
        exit 1
    fi
    echo "依赖检查通过"
}

# 检查数据库连接
check_database() {
    echo "检查数据库连接..."
    cd "$SCRIPT_DIR"
    python3 -c "
from webhook import UserActivityReporter
reporter = UserActivityReporter()
conn = reporter.get_db_connection()
if conn:
    conn.close()
    print('数据库连接正常')
else:
    print('数据库连接失败')
    exit(1)
" 2>/dev/null
    
    if [ $? -ne 0 ]; then
        echo "错误: 数据库连接失败"
        exit 1
    fi
}

# 运行健康检查
health_check() {
    echo "执行健康检查..."
    check_python
    check_dependencies  
    check_database
    echo "健康检查通过"
}

# 运行webhook脚本
run_webhook() {
    cd "$SCRIPT_DIR"
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始执行用户活动日报任务" >> "$LOG_DIR/webhook_runner.log"
    
    # 运行脚本
    timeout 300 python3 "$WEBHOOK_SCRIPT" >> "$LOG_DIR/webhook_runner.log" 2>&1
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 任务执行成功" >> "$LOG_DIR/webhook_runner.log"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 任务执行失败，退出码: $exit_code" >> "$LOG_DIR/webhook_runner.log"
        
        # 发送错误通知
        send_error_notification "用户活动日报任务失败，退出码: $exit_code"
    fi
    
    return $exit_code
}

# 发送错误通知
send_error_notification() {
    local error_msg="$1"
    local current_time=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 构建错误消息
    local notification="⚠️ 系统错误通知
🕐 时间：$current_time
❌ 错误：$error_msg
📂 日志：检查/www/wwwroot/ana/logs/目录"

    # 发送到企业微信
    cd "$SCRIPT_DIR"
    python3 -c "
import requests
import json

url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d3ed6660-1f33-47cc-83dd-84423fc7f8ac'
data = {
    'msgtype': 'text',
    'text': {
        'content': '''$notification'''
    }
}

try:
    response = requests.post(url, json=data, timeout=30)
    if response.status_code == 200:
        result = response.json()
        if result.get('errcode') == 0:
            print('错误通知发送成功')
        else:
            print('错误通知发送失败:', result)
    else:
        print('HTTP请求失败:', response.status_code)
except Exception as e:
    print('发送错误通知失败:', e)
" >> "$LOG_DIR/webhook_runner.log" 2>&1
}

# 主函数
main() {
    case "$1" in
        "health")
            health_check
            ;;
        "run")
            run_webhook
            ;;
        "test")
            health_check
            echo "执行测试..."
            cd "$SCRIPT_DIR"
            python3 test_webhook.py
            ;;
        *)
            echo "用法: $0 {health|run|test}"
            echo ""
            echo "命令说明:"
            echo "  health - 执行健康检查"
            echo "  run    - 运行webhook脚本"  
            echo "  test   - 运行测试脚本"
            echo ""
            echo "生产环境使用示例:"
            echo "  $0 health && $0 run"
            exit 1
            ;;
    esac
}

main "$@"