# 树莓派GPIO控制Web应用

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage->85%25-success)](htmlcov/)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/)

一个功能完整的树莓派GPIO控制Web应用，提供直观的Web界面和实时WebSocket通信，支持GPIO引脚读写、PWM控制等功能。

## ✨ 主要特性

- 🎨 **现代化Web界面** - 美观的GPIO引脚控制面板
- 🔌 **完整GPIO支持** - 支持树莓派40引脚GPIO控制
- ⚡ **实时通信** - 基于WebSocket的实时状态更新
- 🎛️ **PWM控制** - 支持硬件和软件PWM（1Hz-50kHz）
- 📊 **状态监控** - 实时显示引脚状态
- 🔧 **灵活配置** - 多环境配置支持（开发/生产/测试）
- 🧪 **完整测试** - 49+测试用例，覆盖率>85%
- 🛡️ **安全可靠** - GPIO参数验证和自动错误恢复

## 📦 系统要求

- 树莓派（3/4/Zero等）或任何支持GPIO的SBC
- Python 3.7 或更高版本
- 树莓派 OS (Raspbian/Raspberry Pi OS)
- 至少100MB可用磁盘空间

## 🚀 快速开始

### 安装和运行

```bash
# 1. 克隆项目（或使用synctopi.sh同步）
cd /home/pi/gpio

# 2. 运行启动脚本（推荐）
bash start.sh
```

启动脚本会自动：
- 创建Python虚拟环境
- 安装所有依赖
- 启动pigpio守护进程
- 运行Web应用

### 手动安装

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行应用
python run.py
```

### 访问应用

打开浏览器访问: 
- `http://localhost:5000`
- `http://raspberrypi.local:5000`

## 📖 功能说明

### GPIO控制
- ✅ 设置引脚模式（输入/输出/上拉/下拉）
- ✅ 读取引脚状态
- ✅ 写入引脚电平（HIGH/LOW）
- ✅ 切换引脚状态
- ✅ 批量读取所有引脚

### PWM控制
- ✅ 启动PWM输出
- ✅ 调整频率（1Hz - 50kHz）
- ✅ 调整占空比（0-100%）
- ✅ 支持硬件PWM（pigpio）

### 电子元器件演示
- 🎛️ **SG90舵机控制** - 完整的舵机控制演示页面
  - 可视化角度显示和动画
  - 多种控制方式（滑块、快捷按钮、步进、扫描）
  - 实时输出参数监控（角度、脉冲宽度、占空比等）
  - 详见 [SERVO_SG90_DEMO.md](SERVO_SG90_DEMO.md)

### 系统功能
- ✅ 引脚状态实时更新
- ✅ 系统状态监控（`/debug`端点）
- ✅ GPIO重置和清理
- ✅ 错误自动恢复

## 🔧 配置

### 环境变量

```bash
# 运行环境
export FLASK_ENV=development  # 或 production

# 日志级别
export LOG_LEVEL=INFO         # DEBUG, INFO, WARNING, ERROR

# 服务器配置
export HOST=0.0.0.0
export PORT=5000
```

### 配置文件

编辑 `config.py` 来自定义配置：
- `DevelopmentConfig` - 开发环境
- `ProductionConfig` - 生产环境  
- `TestingConfig` - 测试环境

## 📡 API接口

### HTTP端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 主页界面 |
| `/status` | GET | 应用状态 |
| `/debug` | GET | 调试信息 |

### WebSocket事件

| 事件 | 参数 | 说明 |
|------|------|------|
| `gpio_set_mode` | `{pin, mode}` | 设置引脚模式 |
| `gpio_write` | `{pin, value}` | 写入引脚 |
| `gpio_read` | `{pin}` | 读取引脚 |
| `gpio_toggle` | `{pin}` | 切换引脚 |
| `pwm_start` | `{pin, frequency, duty_cycle}` | 启动PWM |
| `pwm_stop` | `{pin}` | 停止PWM |
| `gpio_reset_all` | - | 重置所有引脚 |

## 🧪 测试

### 一键测试（推荐）

```bash
# 在本地运行，自动同步代码到树莓派并执行测试
./test_on_pi.sh

# 测试特定文件
./test_on_pi.sh tests/test_routes.py -v

# 只运行失败的测试
./test_on_pi.sh --lf
```

**注意**: 测试使用Mock，不会影响实际GPIO硬件。

详细测试文档请查看 [TEST_README.md](TEST_README.md)

## 📂 项目结构

```
pi/
├── app/                      # 应用程序
│   ├── __init__.py          # Flask应用和路由
│   ├── gpio_controller.py   # GPIO控制逻辑
│   ├── static/              # 静态文件
│   └── templates/           # HTML模板
├── tests/                   # 测试套件
│   ├── conftest.py         # Pytest配置
│   ├── test_routes.py      # HTTP路由测试
│   ├── test_socketio.py    # WebSocket测试
│   ├── test_gpio_controller.py  # 单元测试
│   └── test_integration.py # 集成测试
├── config.py               # 配置管理
├── run.py                  # 应用入口
├── requirements.txt        # 生产依赖
├── requirements-dev.txt    # 开发/测试依赖
├── start.sh                # 启动脚本
├── synctopi.sh            # 代码同步脚本
└── README.md              # 本文档
```

## 🔒 安全性

### 本地网络使用（当前配置）
- ✅ CORS限制为本地网络
- ✅ PWM参数验证（保护硬件）
- ✅ GPIO状态自动恢复

### 生产环境建议
如需在公网使用，建议：
- 🔒 添加用户认证
- 🔒 使用HTTPS
- 🔒 配置防火墙规则

## 📚 开发

### 安装开发依赖

```bash
pip install -r requirements-dev.txt
```

### 代码检查和格式化

```bash
# 运行测试
pytest

# 生成覆盖率
pytest --cov=app

# 代码格式化（可选）
black app tests
```

### Make命令

```bash
make help          # 显示帮助
make test          # 运行测试
make test-cov      # 测试+覆盖率
make clean         # 清理临时文件
make run           # 运行应用
```

## 🐛 故障排查

### GPIO错误
```bash
# 查看调试信息
curl http://localhost:5000/debug

# 检查pigpio服务
sudo systemctl status pigpiod

# 重启应用
sudo systemctl restart pi-gpio  # 如果使用systemd
```

### 常见问题

**Q: GPIO模式错误**  
A: 应用会自动检测并恢复GPIO状态

**Q: 连接失败**  
A: 检查防火墙和网络设置，确保5000端口开放

**Q: PWM不工作**  
A: 确保pigpio守护进程正在运行：`sudo pigpiod`

**Q: 依赖安装失败**  
A: 升级pip并使用虚拟环境：
```bash
pip install --upgrade pip
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📊 版本历史

### v2.0.2 (当前)
- 🐛 修复测试问题
- 📚 精简文档结构
- ✨ 改进Mock配置

### v2.0.1
- 🧪 完整测试套件
- 📝 详细测试文档

### v2.0.0
- ✨ 配置管理系统
- 🔒 安全性改进
- 📚 完善文档

详见 [CHANGELOG.md](CHANGELOG.md)

## 🤝 贡献

欢迎贡献！请确保：
1. 所有测试通过
2. 代码覆盖率达标
3. 遵循代码风格

## 📝 许可证

MIT License

## 📚 相关文档

- 📖 [TEST_README.md](TEST_README.md) - 测试文档
- 📖 [CHANGELOG.md](CHANGELOG.md) - 版本更新日志
- 🎛️ [SERVO_SG90_DEMO.md](SERVO_SG90_DEMO.md) - SG90舵机控制演示

---

**版本**: v2.0.2  
**最后更新**: 2025-10-08  
**状态**: ✅ 生产就绪