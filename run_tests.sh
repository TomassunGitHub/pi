#!/bin/bash

# 测试运行脚本
# Test runner script

set -e  # Exit on error

echo "🧪 运行树莓派GPIO控制应用测试..."
echo "🧪 Running Raspberry Pi GPIO Control Application Tests..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 激活虚拟环境
if [ -d "venv" ]; then
    echo -e "${GREEN}激活虚拟环境...${NC}"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${GREEN}激活虚拟环境...${NC}"
    source .venv/bin/activate
else
    echo -e "${YELLOW}⚠️  警告: 未找到虚拟环境 (venv)${NC}"
    echo -e "${YELLOW}   建议创建虚拟环境: python3 -m venv venv${NC}"
    echo ""
fi

# 检查是否安装了测试依赖
if ! python -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  pytest未安装，正在安装测试依赖...${NC}"
    pip install -r requirements-dev.txt
    echo ""
fi

# 解析命令行参数
TEST_TYPE="${1:-all}"
VERBOSE=""
COVERAGE="--cov=app --cov-report=term-missing --cov-report=html"

case "$TEST_TYPE" in
    "unit")
        echo -e "${GREEN}运行单元测试...${NC}"
        pytest tests/ -m "not integration" $VERBOSE $COVERAGE
        ;;
    "integration")
        echo -e "${GREEN}运行集成测试...${NC}"
        pytest tests/ -m integration $VERBOSE
        ;;
    "fast")
        echo -e "${GREEN}运行快速测试（无覆盖率）...${NC}"
        pytest tests/ -v
        ;;
    "verbose" | "-v")
        echo -e "${GREEN}运行所有测试（详细模式）...${NC}"
        pytest tests/ -vv -s $COVERAGE
        ;;
    "watch")
        echo -e "${GREEN}监控模式（需要pytest-watch）...${NC}"
        if ! command -v ptw &> /dev/null; then
            echo -e "${YELLOW}安装pytest-watch...${NC}"
            pip install pytest-watch
        fi
        ptw tests/
        ;;
    "help" | "-h" | "--help")
        echo "用法: ./run_tests.sh [选项]"
        echo ""
        echo "选项:"
        echo "  all          - 运行所有测试（默认）"
        echo "  unit         - 只运行单元测试"
        echo "  integration  - 只运行集成测试"
        echo "  fast         - 快速测试（无覆盖率）"
        echo "  verbose, -v  - 详细输出模式"
        echo "  watch        - 监控模式，文件改变时自动运行"
        echo "  help, -h     - 显示此帮助信息"
        echo ""
        echo "示例:"
        echo "  ./run_tests.sh              # 运行所有测试"
        echo "  ./run_tests.sh unit         # 只运行单元测试"
        echo "  ./run_tests.sh verbose      # 详细输出"
        exit 0
        ;;
    *)
        echo -e "${GREEN}运行所有测试...${NC}"
        pytest tests/ $COVERAGE
        ;;
esac

# 检查测试结果
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 所有测试通过！${NC}"
    
    # 如果生成了覆盖率报告，显示链接
    if [ -f "htmlcov/index.html" ]; then
        echo ""
        echo -e "${YELLOW}📊 覆盖率报告已生成:${NC}"
        echo "   file://$(pwd)/htmlcov/index.html"
    fi
    
    exit 0
else
    echo ""
    echo -e "${RED}❌ 测试失败${NC}"
    exit 1
fi
