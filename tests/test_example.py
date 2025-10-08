"""
测试示例文件
Example test file - 展示如何编写新测试
"""

import pytest


class TestExamples:
    """测试示例类"""

    def test_simple_assertion(self):
        """简单断言示例"""
        # Arrange - 准备测试数据
        x = 1
        y = 2

        # Act - 执行操作
        result = x + y

        # Assert - 验证结果
        assert result == 3

    def test_with_fixture(self, client):
        """使用fixture的示例"""
        # 使用client fixture来测试HTTP端点
        response = client.get("/status")
        assert response.status_code == 200

    def test_exception_handling(self):
        """异常处理示例"""
        # 测试是否抛出预期的异常
        with pytest.raises(ValueError):
            int("not_a_number")

    @pytest.mark.parametrize("value,expected", [(1, 2), (2, 4), (3, 6)])
    def test_parametrize_example(self, value, expected):
        """参数化测试示例"""
        # 这个测试会用不同的参数运行多次
        assert value * 2 == expected


# 参数化装饰器示例
@pytest.mark.parametrize(
    "value,expected",
    [
        (1, 2),
        (2, 4),
        (3, 6),
        (10, 20),
    ],
)
def test_multiply_by_two(value, expected):
    """参数化测试：测试乘以2的操作"""
    assert value * 2 == expected


@pytest.mark.unit
def test_marked_as_unit():
    """标记为单元测试的示例"""
    assert True


@pytest.mark.integration
def test_marked_as_integration():
    """标记为集成测试的示例"""
    assert True


@pytest.mark.slow
def test_slow_operation():
    """标记为慢速测试的示例"""
    import time

    time.sleep(0.1)  # 模拟慢速操作
    assert True


def test_dict_comparison():
    """字典比较示例"""
    expected = {"name": "GPIO", "version": "2.0", "status": "ok"}

    actual = {"name": "GPIO", "version": "2.0", "status": "ok"}

    assert actual == expected


def test_list_operations():
    """列表操作测试示例"""
    pins = [17, 18, 22, 23]

    # 测试列表包含
    assert 17 in pins
    assert 99 not in pins

    # 测试列表长度
    assert len(pins) == 4

    # 测试列表排序
    assert pins == sorted(pins)


def test_string_operations():
    """字符串操作测试示例"""
    message = "GPIO pin 17 is HIGH"

    # 字符串包含
    assert "GPIO" in message
    assert "pin 17" in message

    # 字符串方法
    assert message.startswith("GPIO")
    assert message.endswith("HIGH")
    assert message.upper() == "GPIO PIN 17 IS HIGH"


class TestMockingExamples:
    """Mock示例类"""

    def test_with_mock_gpio(self, mock_gpio):
        """使用GPIO mock的示例"""
        # mock_gpio fixture已经配置好了GPIO模拟
        # 可以直接使用
        from app.gpio_controller import GPIOController
        from unittest.mock import MagicMock

        socketio = MagicMock()
        controller = GPIOController(socketio)

        # 测试控制器功能
        assert controller is not None
        assert hasattr(controller, "pin_states")


# 跳过测试示例
@pytest.mark.skip(reason="功能尚未实现")
def test_future_feature():
    """跳过的测试示例"""
    assert False  # 这个测试会被跳过


# 条件跳过示例
@pytest.mark.skipif(not hasattr(pytest, "approx"), reason="需要pytest.approx支持")
def test_conditional_skip():
    """条件跳过示例"""
    assert 0.1 + 0.2 == pytest.approx(0.3)


# 预期失败的测试
@pytest.mark.xfail(reason="已知bug，等待修复")
def test_known_bug():
    """预期失败的测试示例"""
    # 这个测试目前会失败，但标记为xfail
    assert 1 / 0 == 0  # 除零错误


def test_multiple_assertions():
    """多个断言的示例"""
    data = {"pin": 17, "mode": "output", "state": 1}

    # 多个独立的断言
    assert data["pin"] == 17
    assert data["mode"] == "output"
    assert data["state"] == 1
    assert "pull" not in data


def test_with_context():
    """使用上下文的测试示例"""
    # 测试列表操作
    pins = []

    # 添加引脚
    pins.append(17)
    assert len(pins) == 1
    assert 17 in pins

    # 再添加
    pins.extend([18, 22])
    assert len(pins) == 3
    assert pins == [17, 18, 22]


# Fixture示例
@pytest.fixture
def sample_pin_config():
    """返回示例引脚配置的fixture"""
    return {"pin": 17, "mode": "output", "state": 0, "pull": None}


def test_with_custom_fixture(sample_pin_config):
    """使用自定义fixture的示例"""
    # 使用fixture提供的数据
    assert sample_pin_config["pin"] == 17
    assert sample_pin_config["mode"] == "output"
    assert sample_pin_config["state"] == 0


# Setup和teardown示例
class TestSetupTeardown:
    """Setup和Teardown示例"""

    def setup_method(self):
        """每个测试方法执行前调用"""
        self.test_data = [1, 2, 3]

    def teardown_method(self):
        """每个测试方法执行后调用"""
        self.test_data = None

    def test_with_setup(self):
        """使用setup的测试"""
        assert len(self.test_data) == 3
        self.test_data.append(4)
        assert len(self.test_data) == 4

    def test_setup_is_fresh(self):
        """验证每个测试都有新的setup"""
        # 即使上一个测试修改了数据，这里会重新setup
        assert len(self.test_data) == 3
