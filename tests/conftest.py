"""
Pytest configuration and fixtures
"""

import pytest
import sys
from unittest.mock import MagicMock, patch

# Create proper GPIO mocks before importing
rpi_gpio_mock = MagicMock()
rpi_gpio_mock.BCM = 11
rpi_gpio_mock.BOARD = 10
rpi_gpio_mock.IN = 1
rpi_gpio_mock.OUT = 0
rpi_gpio_mock.PUD_UP = 22
rpi_gpio_mock.PUD_DOWN = 21
rpi_gpio_mock.HIGH = 1
rpi_gpio_mock.LOW = 0
rpi_gpio_mock.input.return_value = 1  # Mock GPIO.input() returns integer

# Mock the modules
sys.modules["RPi"] = MagicMock()
sys.modules["RPi.GPIO"] = rpi_gpio_mock
sys.modules["pigpio"] = MagicMock()

from app import create_app
from config import TestingConfig


@pytest.fixture
def app():
    """Create and configure a test application instance"""
    app, socketio = create_app("testing")
    app.config["TESTING"] = True

    yield app


@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()


@pytest.fixture
def socketio_client(app):
    """A test client for SocketIO"""
    from app import create_app

    app, socketio = create_app("testing")

    client = socketio.test_client(app)
    yield client
    client.disconnect()


@pytest.fixture
def mock_gpio():
    """Mock GPIO module for testing"""
    with patch("app.gpio_controller.GPIO_AVAILABLE", True):
        with patch("app.gpio_controller.GPIO") as mock:
            mock.BCM = 11
            mock.IN = 1
            mock.OUT = 0
            mock.PUD_UP = 22
            mock.PUD_DOWN = 21
            mock.HIGH = 1
            mock.LOW = 0
            mock.input.return_value = 1  # Mock GPIO.input() returns integer
            yield mock


@pytest.fixture
def mock_pigpio():
    """Mock pigpio module for testing"""
    with patch("app.gpio_controller.PIGPIO_AVAILABLE", True):
        with patch("app.gpio_controller.pigpio") as mock:
            pi_instance = MagicMock()
            pi_instance.connected = True
            pi_instance.read.return_value = 1  # Mock pi.read() returns integer
            mock.pi.return_value = pi_instance
            mock.INPUT = 0
            mock.OUTPUT = 1
            mock.PUD_UP = 2
            mock.PUD_DOWN = 1
            mock.PUD_OFF = 0
            yield mock, pi_instance
