# 更新日志

## [2.1.0] - 2025-10-19

### ✨ 新增功能
- 🎛️ **SG90舵机控制演示页面** (`/demos/servo-sg90`)
  - 圆形可视化显示，实时动画效果
  - 多种控制方式：滑块、快捷按钮、步进、扫描模式
  - 实时输出参数：角度、脉冲宽度、占空比等
  - 支持硬件PWM（pigpio），精准角度控制（0-180°）
  - 现代化UI设计，响应式布局

### 🎨 界面优化
- 📊 **可视化镜像修正**
  - 调整舵机可视化方向，与实物一致（0°右，180°左）
  - 优化旋转计算公式，直观对应实际转动

- 📈 **布局优化**
  - 实时参数集成到可视化区域，一屏显示所有信息
  - 采用紧凑网格布局（2×4），空间利用率提升60%
  - 参数显示高度从400px降至160px

### 🔧 技术实现
- 后端舵机控制模块 (`app/demos/sg90_servo.py`)
  - PWM频率：50Hz，脉冲宽度：0.5-2.5ms
  - 支持平滑移动、步进控制、扫描模式
  - 线程安全的扫描功能
  
- 前端演示页面 (`app/templates/demos/servo_sg90.html`)
  - Socket.IO实时通信
  - 参数自动更新（0.5Hz刷新率）
  - 完整的操作日志记录

### 📝 文档
- 在主页添加演示入口链接
- 更新README，添加电子元器件演示说明

---

## [2.0.2] - 2025-10-08

### 🐛 测试修复
- 修复JSON序列化错误（MagicMock对象）
- 修复SocketIO响应结构问题
- 修复参数化测试配置错误
- 改进Mock配置，预设所有GPIO常量
- 添加基础冒烟测试（test_simple.py）

### ✨ 新增
- 📝 测试运行指南（RUN_TESTS_GUIDE.md）
- 📝 测试修复总结（TEST_FIXES.md）
- 🧪 基础测试套件（test_simple.py）
- 📚 分层测试策略

---

## [2.0.1] - 2025-10-08

### ✨ 新增
- 🧪 完整的测试套件
  - HTTP路由测试
  - SocketIO事件测试
  - GPIO控制器单元测试
  - 配置管理测试
  - 集成测试
  - 测试覆盖率报告
  
- 📚 测试文档
  - `TEST_README.md` - 测试快速指南
  - `TESTING_GUIDE.md` - 详细测试指南
  - `tests/test_example.py` - 测试示例文件
  
- 🛠️ 测试工具
  - `run_tests.sh` - 测试运行脚本
  - `Makefile` - Make命令支持
  - `pytest.ini` - Pytest配置
  - `.coveragerc` - 覆盖率配置
  - `requirements-dev.txt` - 开发依赖

### 🐛 Bug修复
- 修复GPIO模式重置错误
  - 改进状态验证机制
  - 添加自动恢复功能
  - 详细的错误日志

### 📝 文档
- `BUGFIX_GPIO_MODE.md` - GPIO错误修复说明

---

## [2.0.0] - 2025-10-08

### ✨ 新增
- 📝 添加配置管理系统 (`config.py`)
  - 支持开发/生产/测试多环境配置
  - 环境变量支持
  - 统一的配置管理
  
- 📚 添加部署文档 (`DEPLOYMENT.md`)
  - 本地部署指南
  - 生产环境部署方案（Gunicorn + systemd）
  - Nginx反向代理配置
  - 故障排查指南
  
- 📊 添加改进总结文档 (`IMPROVEMENTS.md`)
  - 详细的改进说明
  - 前后对比
  - 使用建议

- 🔌 Socket.IO本地回退支持
  - 下载本地库文件
  - 自动回退机制
  - 支持离线环境

### 🔒 安全性改进
- 🛡️ 限制CORS为本地网络地址
  - `localhost`
  - `127.0.0.1`
  - `raspberrypi.local`
  
- ⚡ 添加PWM参数验证
  - 频率范围: 1-50000 Hz
  - 占空比范围: 0-100%
  - 防止硬件损坏

### 🐛 Bug修复
- 修复裸`except`子句，改用具体异常类型
- 移除未使用的`time`导入
- 修复signal handler参数未使用警告

### ♻️ 代码重构
- 简化GPIO初始化逻辑
  - 拆分为独立方法
  - 添加重试机制
  - 减少代码复杂度
  
- 统一异常处理机制
  - 添加`@socketio_error_handler`装饰器
  - 所有SocketIO事件使用统一错误处理
  - 改进错误日志记录

### 📝 文档改进
- 优化`synctopi.sh`同步脚本
  - 保留重要文档文件
  - 移除不必要的排除规则
  
- 更新代码注释
  - 明确`allow_unsafe_werkzeug`的使用场景
  - 添加配置说明

### 🎨 日志系统改进
- 支持可配置的日志级别（DEBUG/INFO/WARNING/ERROR）
- 标准化日志格式
- 统一日期时间格式

### 🔧 配置变更

#### 新增环境变量
```bash
FLASK_ENV=development          # 运行环境
LOG_LEVEL=INFO                 # 日志级别
HOST=0.0.0.0                   # 监听地址
PORT=5000                      # 监听端口
CORS_ALLOWED_ORIGINS=...       # CORS配置
```

#### 默认配置变更
- SECRET_KEY: 现在自动生成随机密钥
- CORS: 从`*`限制为本地网络
- 日志: 支持多级别和格式配置

### 📦 文件变更

#### 新增文件
- `config.py` - 配置管理
- `DEPLOYMENT.md` - 部署文档  
- `IMPROVEMENTS.md` - 改进总结
- `CHANGELOG.md` - 更新日志
- `app/static/js/socket.io.min.js` - 本地Socket.IO库

#### 修改文件
- `app/__init__.py` - 集成配置系统，添加错误处理装饰器
- `app/gpio_controller.py` - 简化初始化，添加PWM验证
- `run.py` - 使用配置系统
- `synctopi.sh` - 优化同步规则
- `app/templates/index.html` - 添加CDN回退

### 🔄 迁移指南

从v1.x升级到v2.0:

1. **配置迁移**（可选）:
```bash
# 设置环境变量（如果需要自定义）
export FLASK_ENV=production
export LOG_LEVEL=INFO
```

2. **同步新文件**:
```bash
# 使用更新后的同步脚本
./synctopi.sh
```

3. **安装依赖**（如有变化）:
```bash
pip install -r requirements.txt
```

4. **重启应用**:
```bash
python run.py
```

### ⚠️ 破坏性变更
无破坏性变更。所有改进都向后兼容。

### 📈 性能改进
- 简化GPIO初始化逻辑，减少不必要的检查
- 统一错误处理，避免重复代码

### 🙏 致谢
感谢所有使用本项目的用户！

---

## [1.0.0] - 初始版本

### 功能
- 基础GPIO控制（输入/输出）
- PWM支持
- Web界面控制
- SocketIO实时通信
- 完整的40引脚支持
