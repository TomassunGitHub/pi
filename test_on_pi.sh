#!/bin/bash

# 在树莓派上运行测试脚本
# Sync code to Raspberry Pi and run tests

set -e

# 配置变量
PI_USER="pi"
PI_HOST="raspberrypi"
PI_REMOTE_PATH="/home/pi/gpio"

# SSH配置
SSH_OPTS="-o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=no"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  树莓派测试流程${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 步骤1: 同步代码
echo -e "${YELLOW}📦 步骤 1/2: 同步代码到树莓派...${NC}"
./synctopi.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 代码同步失败${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ 代码同步完成${NC}"
echo ""

# 步骤2: 在树莓派上运行测试脚本
echo -e "${YELLOW}🧪 步骤 2/2: 在树莓派上运行测试...${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 传递所有参数给run_tests.sh
TEST_ARGS="${@:-}"

# 在树莓派上运行测试
ssh ${SSH_OPTS} -t ${PI_USER}@${PI_HOST} << ENDSSH
cd /home/pi/gpio
bash run_tests.sh $TEST_ARGS
ENDSSH

TEST_RESULT=$?

echo ""
echo -e "${BLUE}========================================${NC}"

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ 测试全部通过！${NC}"
    echo ""
    echo -e "${YELLOW}📊 查看覆盖率报告:${NC}"
    echo "   ssh pi@raspberrypi 'cd /home/pi/gpio/htmlcov && python3 -m http.server 8000'"
    echo "   然后在浏览器访问: http://raspberrypi:8000"
    echo ""
    echo -e "${YELLOW}📥 或下载报告到本地:${NC}"
    echo "   scp -r pi@raspberrypi:/home/pi/gpio/htmlcov ./htmlcov_pi"
    echo "   open htmlcov_pi/index.html"
else
    echo -e "${RED}❌ 测试失败${NC}"
    echo ""
    echo -e "${YELLOW}💡 调试建议:${NC}"
    echo "   1. SSH到树莓派查看详细日志:"
    echo "      ssh pi@raspberrypi"
    echo "      cd /home/pi/gpio"
    echo ""
    echo "   2. 运行特定测试:"
    echo "      ./test_on_pi.sh tests/test_routes.py -v"
    echo ""
    echo "   3. 查看可用选项:"
    echo "      ./test_on_pi.sh help"
fi

echo -e "${BLUE}========================================${NC}"
exit $TEST_RESULT

