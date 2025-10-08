# 测试文档

## 📋 测试概览

本项目包含完整的测试套件，所有测试使用Mock模拟GPIO，可安全在树莓派上运行而不影响实际硬件。

### 测试统计
- **测试用例**: 49+ 个
- **代码覆盖率**: >85%
- **测试类型**: HTTP路由、WebSocket事件、单元测试、集成测试

## 🚀 快速开始

### 一键测试（推荐）

```bash
# 在本地机器运行，自动完成：同步代码 + 安装依赖 + 运行测试
./test_on_pi.sh
```

### 手动测试流程

```bash
# 1. 同步代码（在本地机器）
./synctopi.sh

# 2. SSH到树莓派
ssh pi@raspberrypi
cd /home/pi/gpio

# 3. 安装测试依赖
source venv/bin/activate
pip install -r requirements-dev.txt

# 4. 运行测试
pytest

# 5. 生成覆盖率报告
pytest --cov=app --cov-report=html
```

### 查看覆盖率报告

```bash
# 方式1: 在树莓派上启动HTTP服务器
cd htmlcov
python3 -m http.server 8000
# 在本地浏览器访问: http://raspberrypi:8000

# 方式2: 下载到本地查看
scp -r pi@raspberrypi:/home/pi/gpio/htmlcov ./
open htmlcov/index.html
```

## 📂 测试结构

```
tests/
├── conftest.py              # Pytest配置和fixtures
├── test_simple.py           # 基础冒烟测试
├── test_routes.py           # HTTP路由测试（4个）
├── test_socketio.py         # WebSocket事件测试（18个）
├── test_gpio_controller.py  # GPIO控制器单元测试（14个）
├── test_config.py           # 配置管理测试（8个）
├── test_integration.py      # 集成测试（5个）
└── test_example.py          # 测试示例（学习用）
```

## 🧪 测试命令

### 使用test_on_pi.sh（推荐）

```bash
./test_on_pi.sh                               # 运行所有测试
./test_on_pi.sh tests/test_routes.py          # 运行特定文件
./test_on_pi.sh tests/ -v                     # 详细输出
./test_on_pi.sh tests/test_routes.py::TestRoutes::test_debug_endpoint -v
./test_on_pi.sh --lf                          # 只运行失败的测试
./test_on_pi.sh --pdb                         # 调试模式
```

### 在树莓派上直接运行

SSH到树莓派后：

```bash
pytest                          # 运行所有测试
pytest -v                       # 详细输出
pytest -s                       # 显示print输出
pytest -x                       # 遇到第一个错误就停止
```

### 选择性运行

```bash
# 运行特定文件
pytest tests/test_routes.py

# 运行特定测试
pytest tests/test_routes.py::TestRoutes::test_status_endpoint

# 运行匹配的测试
pytest -k "test_gpio"

# 只运行失败的测试
pytest --lf
```

### 覆盖率

```bash
# 显示覆盖率
pytest --cov=app

# 生成HTML报告
pytest --cov=app --cov-report=html

# 显示缺失的行
pytest --cov=app --cov-report=term-missing
```

### 分层测试

```bash
# Level 1: 基础测试（最快）
pytest tests/test_simple.py tests/test_config.py

# Level 2: 单元测试
pytest tests/test_routes.py tests/test_gpio_controller.py

# Level 3: 集成测试（较慢）
pytest tests/test_socketio.py tests/test_integration.py
```

## 🎯 测试覆盖范围

### HTTP端点测试
- ✅ 主页加载 (`/`)
- ✅ 状态查询 (`/status`)
- ✅ 调试信息 (`/debug`)
- ✅ 404错误处理

### SocketIO事件测试
- ✅ 连接/断开
- ✅ GPIO模式设置（input/output/pullup/pulldown）
- ✅ GPIO读写操作
- ✅ PWM控制（启动/停止/参数验证）
- ✅ 批量操作
- ✅ 错误处理

### GPIO控制器测试
- ✅ 初始化和配置
- ✅ 引脚读写操作
- ✅ PWM控制和参数验证
- ✅ 状态管理
- ✅ 错误恢复

### 配置和集成测试
- ✅ 多环境配置
- ✅ 完整工作流
- ✅ 错误恢复机制

## 🔧 Fixtures说明

### `app`
提供测试用Flask应用实例

### `client`
HTTP测试客户端

### `socketio_client`
WebSocket测试客户端

### `mock_gpio`
模拟的RPi.GPIO模块，不影响实际硬件

## ✍️ 编写测试

### 测试模板

```python
"""
Test module description
"""
import pytest


class TestFeature:
    """Test feature description"""

    def test_basic_case(self, client):
        """Test basic functionality"""
        # Arrange - 准备
        data = {'key': 'value'}
        
        # Act - 执行
        response = client.get('/endpoint')
        
        # Assert - 断言
        assert response.status_code == 200

    def test_error_case(self):
        """Test error handling"""
        with pytest.raises(ValueError):
            invalid_operation()
```

### 测试命名规范
- 文件: `test_*.py`
- 类: `Test*`
- 函数: `test_*`

## 🐛 调试测试

### 显示详细信息

```bash
pytest -vv                     # 非常详细的输出
pytest --tb=short              # 简短回溯
pytest -l                      # 显示局部变量
```

### 进入调试器

```bash
pytest --pdb                   # 失败时进入调试器
pytest --pdb --maxfail=1       # 第一次失败就调试
```

### 性能分析

```bash
pytest --durations=10          # 显示最慢的10个测试
pytest --durations=0           # 显示所有测试耗时
```

## ⚠️ 常见问题

### 问题1: pytest找不到

**解决方案**:
```bash
source venv/bin/activate
pip install pytest
```

### 问题2: 导入错误

**解决方案**:
```bash
cd /home/pi/gpio  # 确保在项目根目录
python -m pytest tests/
```

### 问题3: 内存不足（树莓派）

**解决方案**:
```bash
pytest -n 1  # 单进程运行
pytest --no-cov  # 禁用覆盖率
```

### 问题4: Mock不工作

**解决方案**:
- 确保`conftest.py`被正确加载
- 检查Mock配置是否正确

## 📊 预期测试结果

```
tests/test_simple.py ......                      [ 10%]
tests/test_routes.py ....                        [ 18%]
tests/test_config.py ........                    [ 30%]
tests/test_gpio_controller.py ..............     [ 55%]
tests/test_socketio.py ..................        [ 85%]
tests/test_integration.py .....                  [100%]

==================== 49 passed in 5.23s ====================
```

## 💡 最佳实践

1. **测试要快**: 单元测试应在毫秒级完成
2. **测试要独立**: 不依赖其他测试的执行顺序
3. **使用Mock**: 隔离外部依赖（GPIO、网络等）
4. **清晰命名**: 测试名称描述测试内容
5. **测试边界**: 测试边界条件和异常情况
6. **持续更新**: 代码改变时同步更新测试

## 🔍 测试清单

提交代码前确保：
- [ ] 所有测试通过 (`pytest`)
- [ ] 覆盖率达标 (`pytest --cov`)
- [ ] 新功能有对应测试
- [ ] Bug修复有回归测试
- [ ] 测试命名清晰
- [ ] 没有打印调试信息

## 📝 快速命令参考

```bash
# 环境设置
cd /home/pi/gpio
source venv/bin/activate
pip install -r requirements-dev.txt

# 运行测试
pytest                              # 所有测试
pytest -v                           # 详细输出
pytest --cov=app                    # 带覆盖率
pytest tests/test_simple.py         # 特定文件
pytest -k "gpio"                    # 匹配测试
pytest --lf                         # 只运行失败的

# 调试
pytest --pdb                        # 进入调试器
pytest -s                           # 显示print
pytest -vv --tb=long                # 详细错误

# 清理
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
rm -rf .pytest_cache/ htmlcov/ .coverage
```

## 🎓 学习资源

- 查看 `tests/test_example.py` 了解测试写法
- 查看 `tests/test_simple.py` 了解基础测试
- 查看现有测试文件学习实际应用
- [Pytest官方文档](https://docs.pytest.org/)

---

**提示**: 测试完全使用Mock，可以安全运行，不会影响GPIO硬件！