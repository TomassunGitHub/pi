"""
Test SocketIO events
"""

import pytest
from unittest.mock import patch, MagicMock


class TestSocketIOEvents:
    """Test SocketIO event handlers"""

    def test_connect(self, socketio_client):
        """Test client connection"""
        assert socketio_client.is_connected()

    def test_gpio_set_mode_input(self, socketio_client, mock_gpio):
        """Test setting GPIO pin to input mode"""
        socketio_client.emit("gpio_set_mode", {"pin": 17, "mode": "input"})

        received = socketio_client.get_received()
        assert len(received) > 0

        # Find gpio_response in received messages
        response = None
        for msg in received:
            if msg["name"] == "gpio_response":
                response = msg["args"][0] if msg.get("args") else None
                break

        # Response should exist and have expected structure
        assert response is not None
        assert "success" in response

        # If successful, should have pin info
        if response.get("success"):
            assert "pin" in response
            assert response["pin"] == 17

    def test_gpio_set_mode_output(self, socketio_client, mock_gpio):
        """Test setting GPIO pin to output mode"""
        socketio_client.emit("gpio_set_mode", {"pin": 18, "mode": "output"})

        received = socketio_client.get_received()
        assert len(received) > 0

        response = None
        for msg in received:
            if msg["name"] == "gpio_response":
                response = msg["args"][0]
                break

        assert response is not None
        assert "success" in response

    def test_gpio_set_mode_input_pullup(self, socketio_client, mock_gpio):
        """Test setting GPIO pin to input with pull-up"""
        socketio_client.emit("gpio_set_mode", {"pin": 22, "mode": "input_pullup"})

        received = socketio_client.get_received()
        assert len(received) > 0

    def test_gpio_set_mode_missing_params(self, socketio_client):
        """Test setting GPIO mode with missing parameters"""
        socketio_client.emit("gpio_set_mode", {})

        received = socketio_client.get_received()
        assert len(received) > 0

        response = None
        for msg in received:
            if msg["name"] == "gpio_response":
                response = msg["args"][0]
                break

        assert response is not None
        assert response["success"] is False
        assert "error" in response

    def test_gpio_write_high(self, socketio_client, mock_gpio):
        """Test writing HIGH to GPIO pin"""
        socketio_client.emit("gpio_write", {"pin": 23, "value": 1})

        received = socketio_client.get_received()
        assert len(received) > 0

    def test_gpio_write_low(self, socketio_client, mock_gpio):
        """Test writing LOW to GPIO pin"""
        socketio_client.emit("gpio_write", {"pin": 24, "value": 0})

        received = socketio_client.get_received()
        assert len(received) > 0

    def test_gpio_toggle(self, socketio_client, mock_gpio):
        """Test toggling GPIO pin"""
        socketio_client.emit("gpio_toggle", {"pin": 25})

        received = socketio_client.get_received()
        assert len(received) > 0

    def test_gpio_read(self, socketio_client, mock_gpio):
        """Test reading GPIO pin state"""
        socketio_client.emit("gpio_read", {"pin": 26})

        received = socketio_client.get_received()
        assert len(received) > 0

    def test_gpio_read_all(self, socketio_client, mock_gpio):
        """Test reading all GPIO pins"""
        socketio_client.emit("gpio_read_all")

        received = socketio_client.get_received()
        assert len(received) > 0

    def test_pwm_start(self, socketio_client, mock_gpio):
        """Test starting PWM"""
        socketio_client.emit(
            "pwm_start", {"pin": 18, "frequency": 1000, "duty_cycle": 50}
        )

        received = socketio_client.get_received()
        assert len(received) > 0

    def test_pwm_start_invalid_frequency(self, socketio_client, mock_gpio):
        """Test starting PWM with invalid frequency"""
        socketio_client.emit(
            "pwm_start", {"pin": 18, "frequency": 100000, "duty_cycle": 50}  # Too high
        )

        received = socketio_client.get_received()
        response = None
        for msg in received:
            if msg["name"] == "gpio_response":
                response = msg["args"][0]
                break

        assert response is not None
        assert response["success"] is False
        assert "error" in response

    def test_pwm_start_invalid_duty_cycle(self, socketio_client, mock_gpio):
        """Test starting PWM with invalid duty cycle"""
        socketio_client.emit(
            "pwm_start", {"pin": 18, "frequency": 1000, "duty_cycle": 150}  # Too high
        )

        received = socketio_client.get_received()
        response = None
        for msg in received:
            if msg["name"] == "gpio_response":
                response = msg["args"][0]
                break

        assert response is not None
        assert response["success"] is False

    def test_pwm_stop(self, socketio_client, mock_gpio):
        """Test stopping PWM"""
        # First start PWM
        socketio_client.emit(
            "pwm_start", {"pin": 18, "frequency": 1000, "duty_cycle": 50}
        )
        socketio_client.get_received()  # Clear received messages

        # Then stop it
        socketio_client.emit("pwm_stop", {"pin": 18})

        received = socketio_client.get_received()
        assert len(received) > 0

    def test_gpio_reset_all(self, socketio_client, mock_gpio):
        """Test resetting all GPIO pins"""
        socketio_client.emit("gpio_reset_all")

        received = socketio_client.get_received()
        assert len(received) > 0

    def test_gpio_cleanup(self, socketio_client, mock_gpio):
        """Test GPIO cleanup"""
        socketio_client.emit("gpio_cleanup")

        received = socketio_client.get_received()
        assert len(received) > 0

        response = None
        for msg in received:
            if msg["name"] == "gpio_response":
                response = msg["args"][0]
                break

        assert response is not None
        assert response["success"] is True

    def test_get_pin_info(self, socketio_client, mock_gpio):
        """Test getting pin information"""
        # First configure a pin
        socketio_client.emit("gpio_set_mode", {"pin": 27, "mode": "output"})
        socketio_client.get_received()  # Clear messages

        # Then get info
        socketio_client.emit("get_pin_info", {"pin": 27})

        received = socketio_client.get_received()
        assert len(received) > 0
