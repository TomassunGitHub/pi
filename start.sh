#!/bin/bash

# 树莓派3应用启动脚本
# Raspberry Pi 3 Application Startup Script

echo "🍓 启动树莓派3控制应用..."
echo "🍓 Starting Raspberry Pi 3 Control Application..."

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    echo "❌ Error: Python3 not found"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."

    # 尝试创建虚拟环境，如果失败则尝试其他方法
    if ! python3 -m venv venv 2>/dev/null; then
        echo "⚠️  标准venv创建失败，尝试使用--without-pip选项..."
        python3 -m venv --without-pip venv

        echo "📦 手动安装pip..."
        source venv/bin/activate

        # 尝试多种方法安装pip
        if command -v curl &> /dev/null; then
            curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
            python get-pip.py
            rm get-pip.py
        elif command -v wget &> /dev/null; then
            wget https://bootstrap.pypa.io/get-pip.py
            python get-pip.py
            rm get-pip.py
        else
            echo "❌ 无法安装pip，请手动安装"
            echo "💡 尝试运行: sudo apt install python3-pip python3-venv"
            exit 1
        fi
    fi

    echo "✅ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📚 安装依赖包..."
pip install -r requirements.txt

# 启动pigpio服务 (如果在树莓派上)
if [ -f "/proc/device-tree/model" ] && grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo "🔌 检测到树莓派硬件，检查pigpio服务状态..."
    # 检查pigpiod是否已经在运行
    if pgrep -x "pigpiod" > /dev/null; then
        echo "✅ pigpiod服务已在运行"
    else
        echo "🚀 启动pigpio服务..."
        # 尝试启动pigpiod服务
        if sudo systemctl start pigpiod 2>/dev/null; then
            echo "✅ 通过systemctl启动pigpiod成功"
            # 设置开机自启
            sudo systemctl enable pigpiod 2>/dev/null
        else
            # 如果systemctl失败，尝试直接启动pigpiod
            echo "⚠️  systemctl启动失败，尝试直接启动pigpiod..."
            if sudo pigpiod 2>/dev/null; then
                echo "✅ 直接启动pigpiod成功"
            else
                echo "❌ 启动pigpiod失败，GPIO功能可能不可用"
                echo "💡 请检查pigpio是否已安装: sudo apt install pigpio"
            fi
        fi
        # 等待服务启动
        sleep 2
        # 验证服务是否成功启动
        if pgrep -x "pigpiod" > /dev/null; then
            echo "✅ pigpiod服务启动成功"
        else
            echo "⚠️  pigpiod服务可能启动失败，GPIO功能可能受限"
        fi
    fi
else
    echo "ℹ️  非树莓派环境，跳过pigpio服务启动"
fi

# 启动应用
echo "🚀 启动Web应用..."
echo "🌐 访问地址: http://localhost:5000"
echo "🌐 Access URL: http://localhost:5000"

# 日志文件路径
LOG_FILE="logs/app.log"
mkdir -p logs

# 检查是否后台运行
if [ "$1" = "--daemon" ] || [ "$1" = "-d" ]; then
    echo "📝 后台运行模式，日志输出到: $LOG_FILE"
    echo "🔍 查看日志: tail -f $LOG_FILE"
    echo "🛑 停止服务: pkill -f 'python.*run.py'"
    nohup python run.py > "$LOG_FILE" 2>&1 &
    PID=$!
    echo "✅ 应用已在后台启动，PID: $PID"
else
    echo "📝 前台运行模式，日志同时输出到控制台和文件: $LOG_FILE"
    echo "按 Ctrl+C 停止应用 / Press Ctrl+C to stop"
    echo ""
    python run.py 2>&1 | tee "$LOG_FILE"
fi