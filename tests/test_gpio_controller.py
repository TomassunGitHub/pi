"""
Test GPIO Controller
"""

import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock modules before importing
sys.modules["RPi"] = MagicMock()
sys.modules["RPi.GPIO"] = MagicMock()
sys.modules["pigpio"] = MagicMock()

from app.gpio_controller import GPIOController


class TestGPIOController:
    """Test GPIOController class"""

    @pytest.fixture
    def controller(self):
        """Create a GPIO controller instance for testing"""
        socketio = MagicMock()
        with patch("app.gpio_controller.GPIO_AVAILABLE", True):
            with patch("app.gpio_controller.GPIO") as mock_gpio:
                mock_gpio.BCM = 11
                mock_gpio.IN = 1
                mock_gpio.OUT = 0
                controller = GPIOController(socketio)
                yield controller

    def test_initialization(self, controller):
        """Test controller initialization"""
        assert controller is not None
        assert hasattr(controller, "pin_states")
        assert hasattr(controller, "pwm_instances")
        assert isinstance(controller.pin_states, dict)
        assert isinstance(controller.pwm_instances, dict)

    def test_setup_pin_output(self, controller):
        """Test setting up a pin as output"""
        with patch("app.gpio_controller.GPIO") as mock_gpio:
            mock_gpio.BCM = 11
            mock_gpio.OUT = 0

            result = controller.setup_pin(17, "output")

            assert "success" in result
            assert result["pin"] == 17
            assert result["mode"] == "output"

    def test_setup_pin_input(self, controller):
        """Test setting up a pin as input"""
        with patch("app.gpio_controller.GPIO") as mock_gpio:
            mock_gpio.BCM = 11
            mock_gpio.IN = 1

            result = controller.setup_pin(18, "input")

            assert "success" in result
            assert result["pin"] == 18
            assert result["mode"] == "input"

    def test_setup_pin_input_pullup(self, controller):
        """Test setting up a pin as input with pull-up"""
        with patch("app.gpio_controller.GPIO") as mock_gpio:
            mock_gpio.BCM = 11
            mock_gpio.IN = 1
            mock_gpio.PUD_UP = 22

            result = controller.setup_pin(22, "input", "pullup")

            assert "success" in result
            assert result["pin"] == 22

    def test_write_pin(self, controller):
        """Test writing to a pin"""
        with patch("app.gpio_controller.GPIO") as mock_gpio:
            result = controller.write_pin(23, 1)

            assert "success" in result
            assert result["pin"] == 23
            assert result["state"] == 1

    def test_read_pin(self, controller):
        """Test reading from a pin"""
        with patch("app.gpio_controller.GPIO") as mock_gpio:
            mock_gpio.input.return_value = 1

            result = controller.read_pin(24)

            assert "success" in result
            assert result["pin"] == 24

    def test_toggle_pin(self, controller):
        """Test toggling a pin"""
        with patch("app.gpio_controller.GPIO") as mock_gpio:
            # Set initial state
            controller.pin_states[25] = {"mode": "output", "state": 0}

            result = controller.toggle_pin(25)

            assert "success" in result
            assert result["pin"] == 25

    def test_start_pwm_valid_params(self, controller):
        """Test starting PWM with valid parameters"""
        with patch("app.gpio_controller.GPIO") as mock_gpio:
            mock_pwm = MagicMock()
            mock_gpio.PWM.return_value = mock_pwm

            result = controller.start_pwm(18, 1000, 50)

            assert "success" in result
            assert result["pin"] == 18
            assert result["frequency"] == 1000
            assert result["duty_cycle"] == 50

    def test_start_pwm_invalid_frequency(self, controller):
        """Test starting PWM with invalid frequency"""
        result = controller.start_pwm(18, 100000, 50)  # Too high

        assert result["success"] is False
        assert "error" in result
        assert "frequency" in result["error"].lower()

    def test_start_pwm_invalid_duty_cycle(self, controller):
        """Test starting PWM with invalid duty cycle"""
        result = controller.start_pwm(18, 1000, 150)  # Too high

        assert result["success"] is False
        assert "error" in result
        assert "duty" in result["error"].lower()

    def test_stop_pwm(self, controller):
        """Test stopping PWM"""
        # First start PWM
        controller.pwm_instances[18] = {
            "type": "rpi_gpio",
            "instance": MagicMock(),
            "frequency": 1000,
            "duty_cycle": 50,
        }

        result = controller.stop_pwm(18)

        assert result["success"] is True
        assert result["pin"] == 18

    def test_reset_all_pins(self, controller):
        """Test resetting all pins"""
        with patch("app.gpio_controller.GPIO") as mock_gpio:
            controller.pin_states[17] = {"mode": "output", "state": 1}

            result = controller.reset_all_pins()

            assert result["success"] is True
            assert len(controller.pin_states) == 0

    def test_get_pin_info(self, controller):
        """Test getting pin information"""
        controller.pin_states[26] = {"mode": "output", "state": 1, "pull": None}

        info = controller.get_pin_info(26)

        assert info["pin"] == 26
        assert info["mode"] == "output"
        assert info["state"] == 1

    def test_get_system_status(self, controller):
        """Test getting system status"""
        status = controller.get_system_status()

        assert "gpio_available" in status
        assert "gpio_initialized" in status
        assert "configured_pins" in status
        assert "active_pwm" in status
