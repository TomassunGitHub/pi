"""
Integration tests for complete workflows
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.mark.integration
class TestIntegrationWorkflows:
    """Test complete user workflows"""

    def test_complete_gpio_workflow(self, socketio_client, mock_gpio):
        """Test complete GPIO workflow: configure -> write -> read -> cleanup"""

        # Step 1: Configure pin as output
        socketio_client.emit("gpio_set_mode", {"pin": 17, "mode": "output"})
        received = socketio_client.get_received()
        assert len(received) > 0

        # Step 2: Write HIGH
        socketio_client.emit("gpio_write", {"pin": 17, "value": 1})
        received = socketio_client.get_received()
        assert len(received) > 0

        # Step 3: Read state
        socketio_client.emit("gpio_read", {"pin": 17})
        received = socketio_client.get_received()
        assert len(received) > 0

        # Step 4: Write LOW
        socketio_client.emit("gpio_write", {"pin": 17, "value": 0})
        received = socketio_client.get_received()
        assert len(received) > 0

        # Step 5: Cleanup
        socketio_client.emit("gpio_cleanup")
        received = socketio_client.get_received()
        assert len(received) > 0

    def test_pwm_workflow(self, socketio_client, mock_gpio):
        """Test PWM workflow: configure -> start PWM -> adjust -> stop"""

        # Step 1: Configure pin as output
        socketio_client.emit("gpio_set_mode", {"pin": 18, "mode": "output"})
        socketio_client.get_received()

        # Step 2: Start PWM
        socketio_client.emit(
            "pwm_start", {"pin": 18, "frequency": 1000, "duty_cycle": 50}
        )
        received = socketio_client.get_received()
        assert len(received) > 0

        # Step 3: Adjust PWM
        socketio_client.emit(
            "pwm_start", {"pin": 18, "frequency": 2000, "duty_cycle": 75}
        )
        received = socketio_client.get_received()
        assert len(received) > 0

        # Step 4: Stop PWM
        socketio_client.emit("pwm_stop", {"pin": 18})
        received = socketio_client.get_received()
        assert len(received) > 0

    def test_multiple_pins_workflow(self, socketio_client, mock_gpio):
        """Test managing multiple pins simultaneously"""

        # Configure multiple pins
        pins = [17, 18, 22, 23]

        for pin in pins:
            socketio_client.emit("gpio_set_mode", {"pin": pin, "mode": "output"})
            socketio_client.get_received()

        # Write to all pins
        for i, pin in enumerate(pins):
            socketio_client.emit(
                "gpio_write", {"pin": pin, "value": i % 2}  # Alternate HIGH/LOW
            )
            socketio_client.get_received()

        # Read all pins
        socketio_client.emit("gpio_read_all")
        received = socketio_client.get_received()
        assert len(received) > 0

        # Reset all
        socketio_client.emit("gpio_reset_all")
        received = socketio_client.get_received()
        assert len(received) > 0

    def test_error_recovery_workflow(self, socketio_client, mock_gpio):
        """Test error recovery after GPIO reset"""

        # Step 1: Normal operation
        socketio_client.emit("gpio_set_mode", {"pin": 24, "mode": "output"})
        socketio_client.get_received()

        # Step 2: Reset all (simulates GPIO cleanup)
        socketio_client.emit("gpio_reset_all")
        socketio_client.get_received()

        # Step 3: Try to use pin again (should reinitialize automatically)
        socketio_client.emit("gpio_set_mode", {"pin": 24, "mode": "output"})
        received = socketio_client.get_received()
        assert len(received) > 0

    def test_web_interface_loading(self, client):
        """Test that web interface loads correctly"""
        # Load main page
        response = client.get("/")
        assert response.status_code == 200

        # Check status
        response = client.get("/status")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"

        # Check debug endpoint exists (may return ok or error)
        response = client.get("/debug")
        assert response.status_code == 200
        assert response.content_type == "application/json"
