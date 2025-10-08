#!/bin/bash

# 树莓派同步脚本
# 使用rsync将当前目录的所有文件同步到树莓派

# 配置变量
PI_USER="pi"
PI_HOST="raspberrypi"
PI_REMOTE_PATH="/home/pi/gpio"
LOCAL_PATH="/Users/sunfaxu/python/pi"

# SSH配置
SSH_OPTS="-o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=no"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}开始同步文件到树莓派...${NC}"
echo "源目录: $(pwd)"
echo "目标: ${PI_USER}@${PI_HOST}:${PI_REMOTE_PATH}"
echo ""

# 检查SSH连接和公钥认证
echo -e "${YELLOW}检查SSH公钥认证连接...${NC}"
if ! ssh ${SSH_OPTS} ${PI_USER}@${PI_HOST} "echo 'SSH连接测试成功'" > /dev/null 2>&1; then
    echo -e "${RED}错误: SSH公钥认证连接失败${NC}"
    echo "请检查："
    echo "1. SSH公钥是否已正确配置到树莓派的 ~/.ssh/authorized_keys"
    echo "2. 树莓派SSH服务是否正在运行"
    echo "3. 主机名 'raspberrypi' 是否可以解析"
    echo "4. 可以尝试手动测试: ssh ${PI_USER}@${PI_HOST}"
    exit 1
fi

echo -e "${GREEN}SSH公钥认证连接正常${NC}"
echo ""

# 创建远程目录（如果不存在）
echo -e "${YELLOW}确保远程目录存在...${NC}"
ssh ${SSH_OPTS} ${PI_USER}@${PI_HOST} "mkdir -p ${PI_REMOTE_PATH}"

if [ $? -ne 0 ]; then
    echo -e "${RED}错误: 无法创建远程目录${NC}"
    echo "请检查远程目录权限和SSH连接"
    exit 1
fi

# 使用rsync同步文件
echo -e "${YELLOW}开始同步文件...${NC}"

# rsync参数说明：
# -a: 归档模式，保持文件属性
# -v: 详细输出
# -z: 压缩传输
# -h: 人类可读的输出格式
# --progress: 显示进度
# --delete: 删除目标目录中源目录没有的文件
# --exclude: 排除指定文件/目录

rsync -avzh --progress --delete \
    -e "ssh ${SSH_OPTS}" \
    --exclude='.git/' \
    --exclude='.vscode/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='node_modules/' \
    --exclude='.env' \
    --exclude='venv/' \
    --exclude='.pytest_cache/' \
    --exclude='*.log' \
    --exclude='.gitignore' \
    --exclude='htmlcov/' \
    --exclude='.coverage' \
    --exclude='.coverage.*' \
    ${LOCAL_PATH}/ ${PI_USER}@${PI_HOST}:${PI_REMOTE_PATH}/

# 检查同步结果
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 文件同步完成！${NC}"
    echo "所有文件已成功同步到 ${PI_USER}@${PI_HOST}:${PI_REMOTE_PATH}"
else
    echo ""
    echo -e "${RED}❌ 同步过程中出现错误${NC}"
    exit 1
fi

# 可选：显示远程目录内容
echo ""
echo -e "${YELLOW}远程目录内容：${NC}"
ssh ${SSH_OPTS} ${PI_USER}@${PI_HOST} "ls -la ${PI_REMOTE_PATH}"

echo ""
echo -e "${GREEN}同步脚本执行完成！${NC}"
