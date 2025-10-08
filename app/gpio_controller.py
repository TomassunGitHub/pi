import logging
from typing import Dict, Any

try:
    import RPi.GPIO as GPIO

    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO not available. Running in simulation mode.")

try:
    import pigpio

    PIGPIO_AVAILABLE = True
except ImportError:
    PIGPIO_AVAILABLE = False
    logging.warning("pigpio not available. Using RPi.GPIO fallback.")


class GPIOController:
    def __init__(self, socketio):
        self.socketio = socketio
        self.logger = logging.getLogger(__name__)
        self.pin_states = {}
        self.pwm_instances = {}
        self.gpio_initialized = False

        self._initialize_gpio()

    def _initialize_gpio(self):
        """Initialize GPIO settings"""
        if GPIO_AVAILABLE:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                self.gpio_initialized = True
                self.logger.info("GPIO initialized with BCM mode")
            except Exception as e:
                self.logger.error(f"Failed to initialize GPIO: {e}")
                self.gpio_initialized = False

        if PIGPIO_AVAILABLE:
            try:
                self.pi = pigpio.pi()
                if not self.pi.connected:
                    self.logger.warning(
                        "pigpio daemon not running. Using simulation mode."
                    )
                    self.pi = None
                else:
                    self.logger.info("pigpio connected successfully")
            except Exception as e:
                self.pi = None
                self.logger.warning(f"Failed to connect to pigpio daemon: {e}")

    def _ensure_gpio_initialized(self):
        """Ensure GPIO is properly initialized"""
        if not GPIO_AVAILABLE:
            return True

        # If marked as initialized, verify it's actually working
        if self.gpio_initialized:
            try:
                # Test if GPIO mode is still set by calling setmode again
                # This will succeed silently if already set correctly
                GPIO.setmode(GPIO.BCM)
                return True
            except RuntimeError as e:
                # GPIO was cleaned up externally, need to reinitialize
                self.logger.warning(f"GPIO state lost, reinitializing: {e}")
                self.gpio_initialized = False

        return self._initialize_gpio_with_retry()

    def _initialize_gpio_with_retry(self, retry_with_cleanup=True):
        """Initialize GPIO with optional cleanup retry"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            self.gpio_initialized = True
            self.logger.info("GPIO initialized with BCM mode")
            return True
        except Exception as e:
            if retry_with_cleanup:
                self.logger.warning(f"GPIO init failed ({e}), retrying with cleanup...")
                try:
                    GPIO.cleanup()
                    return self._initialize_gpio_with_retry(retry_with_cleanup=False)
                except Exception as e2:
                    self.logger.error(f"GPIO init failed after cleanup: {e2}")
            else:
                self.logger.error(f"GPIO initialization failed: {e}")

            self.gpio_initialized = False
            return False

    def _emit_to_clients(self, event: str, data: dict):
        """Safely emit data to clients (optional, mainly for real-time updates)"""
        try:
            # Only emit if socketio is available and we're in a request context
            if self.socketio and hasattr(self.socketio, "emit"):
                try:
                    self.socketio.emit(event, data, broadcast=True)
                except (RuntimeError, AttributeError, TypeError) as e:
                    # Expected when called outside request context or with invalid socketio object
                    # This is not an error - events will be sent via normal response flow
                    pass
            else:
                # SocketIO not configured - not an error in test mode
                pass
        except Exception as e:
            # Log but don't fail - emit is optional for real-time updates
            # This catches any unexpected errors to prevent breaking the main functionality
            self.logger.debug(f"Optional real-time emit skipped for {event}: {e}")

    def setup_pin(
        self, pin: int, mode: str, pull_up_down: str = None
    ) -> Dict[str, Any]:
        """Setup a GPIO pin for input or output with optional pull-up/down"""
        try:
            # Ensure GPIO is initialized
            if not self._ensure_gpio_initialized():
                return {
                    "success": False,
                    "pin": pin,
                    "error": "GPIO initialization failed",
                }

            if GPIO_AVAILABLE:
                try:
                    if mode == "input":
                        if pull_up_down == "pullup":
                            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                        elif pull_up_down == "pulldown":
                            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                        else:
                            GPIO.setup(pin, GPIO.IN)
                    elif mode == "output":
                        GPIO.setup(pin, GPIO.OUT)
                except RuntimeError as e:
                    # If GPIO mode was not set, try to reinitialize
                    if "pin numbering mode" in str(e).lower():
                        self.logger.warning(f"GPIO mode was reset, reinitializing: {e}")
                        self.gpio_initialized = False
                        if not self._initialize_gpio_with_retry():
                            return {
                                "success": False,
                                "pin": pin,
                                "error": f"Failed to reinitialize GPIO: {e}",
                            }
                        # Retry the setup after reinitialization
                        if mode == "input":
                            if pull_up_down == "pullup":
                                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                            elif pull_up_down == "pulldown":
                                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                            else:
                                GPIO.setup(pin, GPIO.IN)
                        elif mode == "output":
                            GPIO.setup(pin, GPIO.OUT)
                    else:
                        raise

            if self.pi and PIGPIO_AVAILABLE:
                if mode == "input":
                    self.pi.set_mode(pin, pigpio.INPUT)
                    if pull_up_down == "pullup":
                        self.pi.set_pull_up_down(pin, pigpio.PUD_UP)
                    elif pull_up_down == "pulldown":
                        self.pi.set_pull_up_down(pin, pigpio.PUD_DOWN)
                    else:
                        self.pi.set_pull_up_down(pin, pigpio.PUD_OFF)
                elif mode == "output":
                    self.pi.set_mode(pin, pigpio.OUTPUT)

            # Read initial state
            initial_state = 0
            if mode == "input":
                initial_state = self.read_pin_value(pin)

            self.pin_states[pin] = {
                "mode": mode,
                "state": initial_state,
                "pull": pull_up_down,
            }
            self.logger.info(
                f"Pin {pin} setup as {mode}"
                + (f" with {pull_up_down}" if pull_up_down else "")
            )

            return {
                "success": True,
                "pin": pin,
                "mode": mode,
                "state": initial_state,
                "message": f"Pin {pin} configured as {mode}"
                + (f" with {pull_up_down}" if pull_up_down else ""),
            }
        except Exception as e:
            self.logger.error(f"Error setting up pin {pin}: {str(e)}")
            return {"success": False, "pin": pin, "error": str(e)}

    def read_pin_value(self, pin: int) -> int:
        """Read the actual hardware state of a pin"""
        try:
            if GPIO_AVAILABLE:
                return GPIO.input(pin)
            elif self.pi and PIGPIO_AVAILABLE:
                return self.pi.read(pin)
            else:
                # Simulation mode - return cached state or 0
                return self.pin_states.get(pin, {}).get("state", 0)
        except Exception as e:
            self.logger.error(f"Error reading pin {pin} value: {e}")
            return 0

    def set_pin_mode(self, pin: int, mode: str) -> Dict[str, Any]:
        """Set pin mode (input/output/input_pullup/input_pulldown)"""
        pull_up_down = None
        if mode == "input_pullup":
            mode = "input"
            pull_up_down = "pullup"
        elif mode == "input_pulldown":
            mode = "input"
            pull_up_down = "pulldown"

        return self.setup_pin(pin, mode, pull_up_down)

    def write_pin(self, pin: int, value: int) -> Dict[str, Any]:
        """Write a value to a GPIO pin"""
        try:
            # Ensure GPIO is initialized
            if not self._ensure_gpio_initialized():
                return {
                    "success": False,
                    "pin": pin,
                    "error": "GPIO initialization failed",
                }

            # Ensure pin is set up as output
            if pin not in self.pin_states or self.pin_states[pin]["mode"] != "output":
                result = self.setup_pin(pin, "output")
                if not result["success"]:
                    return result

            if GPIO_AVAILABLE:
                GPIO.output(pin, value)

            if self.pi and PIGPIO_AVAILABLE:
                self.pi.write(pin, value)

            self.pin_states[pin]["state"] = value
            self.logger.info(f"Pin {pin} set to {value}")

            # Optional: Emit state change for real-time updates (may fail outside request context)
            self._emit_to_clients(
                "pin_state_changed", {"pin": pin, "state": value, "mode": "output"}
            )

            return {
                "success": True,
                "pin": pin,
                "state": value,
                "mode": "output",
                "message": f'Pin {pin} set to {"HIGH" if value else "LOW"}',
            }
        except Exception as e:
            self.logger.error(f"Error writing to pin {pin}: {str(e)}")
            return {"success": False, "pin": pin, "error": str(e)}

    def toggle_pin(self, pin: int) -> Dict[str, Any]:
        """Toggle a GPIO pin output"""
        try:
            if pin not in self.pin_states:
                # Auto-setup as output if not configured
                result = self.setup_pin(pin, "output")
                if not result["success"]:
                    return result

            current_state = self.pin_states[pin]["state"]
            new_state = 1 - current_state

            return self.write_pin(pin, new_state)
        except Exception as e:
            self.logger.error(f"Error toggling pin {pin}: {str(e)}")
            return {"success": False, "pin": pin, "error": str(e)}

    def read_pin(self, pin: int) -> Dict[str, Any]:
        """Read a GPIO pin state"""
        try:
            if pin not in self.pin_states:
                # Auto-setup as input if not configured
                result = self.setup_pin(pin, "input")
                if not result["success"]:
                    return result

            state = self.read_pin_value(pin)
            self.pin_states[pin]["state"] = state
            self.logger.info(f"Pin {pin} read as {state}")

            return {
                "success": True,
                "pin": pin,
                "state": state,
                "mode": self.pin_states[pin]["mode"],
                "message": f'Pin {pin} is {"HIGH" if state else "LOW"}',
            }
        except Exception as e:
            self.logger.error(f"Error reading pin {pin}: {str(e)}")
            return {"success": False, "pin": pin, "error": str(e)}

    def read_all_pins(self) -> Dict[str, Any]:
        """Read all configured GPIO pins"""
        try:
            # Ensure GPIO is initialized
            if not self._ensure_gpio_initialized():
                return {"success": False, "error": "GPIO initialization failed"}

            all_states = {}
            for pin in self.pin_states:
                state = self.read_pin_value(pin)
                self.pin_states[pin]["state"] = state
                all_states[pin] = {
                    "state": state,
                    "mode": self.pin_states[pin]["mode"],
                    "pull": self.pin_states[pin].get("pull"),
                }

            self.logger.info(f"Read all pins: {len(all_states)} pins")

            # Optional: Emit for real-time updates (may fail outside request context)
            self._emit_to_clients("all_pins_state", all_states)

            return {
                "success": True,
                "states": all_states,
                "message": f"Read {len(all_states)} pins",
            }
        except Exception as e:
            self.logger.error(f"Error reading all pins: {str(e)}")
            return {"success": False, "error": str(e)}

    def start_pwm(self, pin: int, frequency: int, duty_cycle: int) -> Dict[str, Any]:
        """Start PWM output on a pin"""
        try:
            # Validate PWM parameters
            if not isinstance(frequency, (int, float)) or frequency <= 0:
                return {
                    "success": False,
                    "pin": pin,
                    "error": f"Invalid frequency: {frequency}. Must be a positive number.",
                }

            if frequency > 50000:
                return {
                    "success": False,
                    "pin": pin,
                    "error": f"Frequency {frequency}Hz exceeds maximum safe limit (50kHz).",
                }

            if (
                not isinstance(duty_cycle, (int, float))
                or duty_cycle < 0
                or duty_cycle > 100
            ):
                return {
                    "success": False,
                    "pin": pin,
                    "error": f"Invalid duty cycle: {duty_cycle}. Must be between 0 and 100.",
                }

            # Ensure GPIO is initialized
            if not self._ensure_gpio_initialized():
                return {
                    "success": False,
                    "pin": pin,
                    "error": "GPIO initialization failed",
                }

            # Ensure pin is set up as output
            if pin not in self.pin_states or self.pin_states[pin]["mode"] != "output":
                result = self.setup_pin(pin, "output")
                if not result["success"]:
                    return result

            # Stop existing PWM if running
            if pin in self.pwm_instances:
                self.stop_pwm_pin(pin)

            if self.pi and PIGPIO_AVAILABLE:
                # Use hardware PWM for better performance
                self.pi.hardware_PWM(
                    pin, frequency, duty_cycle * 10000
                )  # duty_cycle in microseconds
                self.pwm_instances[pin] = {
                    "type": "pigpio",
                    "frequency": frequency,
                    "duty_cycle": duty_cycle,
                }
            elif GPIO_AVAILABLE:
                # Use software PWM
                pwm = GPIO.PWM(pin, frequency)
                pwm.start(duty_cycle)
                self.pwm_instances[pin] = {
                    "type": "rpi_gpio",
                    "instance": pwm,
                    "frequency": frequency,
                    "duty_cycle": duty_cycle,
                }

            self.logger.info(f"Pin {pin} PWM started: {frequency}Hz, {duty_cycle}%")

            return {
                "success": True,
                "pin": pin,
                "frequency": frequency,
                "duty_cycle": duty_cycle,
                "message": f"Pin {pin} PWM started: {frequency}Hz, {duty_cycle}%",
            }
        except Exception as e:
            self.logger.error(f"Error starting PWM on pin {pin}: {str(e)}")
            return {"success": False, "pin": pin, "error": str(e)}

    def stop_pwm(self, pin: int) -> Dict[str, Any]:
        """Stop PWM output on a pin"""
        try:
            if pin not in self.pwm_instances:
                return {
                    "success": False,
                    "pin": pin,
                    "error": "PWM not running on this pin",
                }

            self.stop_pwm_pin(pin)
            self.logger.info(f"Pin {pin} PWM stopped")

            return {"success": True, "pin": pin, "message": f"Pin {pin} PWM stopped"}
        except Exception as e:
            self.logger.error(f"Error stopping PWM on pin {pin}: {str(e)}")
            return {"success": False, "pin": pin, "error": str(e)}

    def stop_pwm_pin(self, pin: int):
        """Internal method to stop PWM on a specific pin"""
        if pin in self.pwm_instances:
            pwm_info = self.pwm_instances[pin]
            if pwm_info["type"] == "pigpio" and self.pi and PIGPIO_AVAILABLE:
                self.pi.hardware_PWM(pin, 0, 0)  # Stop hardware PWM
            elif pwm_info["type"] == "rpi_gpio" and "instance" in pwm_info:
                pwm_info["instance"].stop()
            del self.pwm_instances[pin]

    def reset_all_pins(self) -> Dict[str, Any]:
        """Reset all GPIO pins to their default state"""
        try:
            # Stop all PWM
            for pin in list(self.pwm_instances.keys()):
                self.stop_pwm_pin(pin)

            # Reset all pin states
            self.pin_states.clear()

            if GPIO_AVAILABLE:
                try:
                    GPIO.cleanup()
                    self.logger.info("GPIO cleanup completed")
                except Exception as e:
                    self.logger.warning(f"GPIO cleanup warning: {e}")
                finally:
                    # Mark as uninitialized so it will be re-initialized on next use
                    self.gpio_initialized = False

            self.logger.info("All GPIO pins reset")

            return {"success": True, "message": "All GPIO pins reset"}
        except Exception as e:
            self.logger.error(f"Error resetting pins: {str(e)}")
            return {"success": False, "error": str(e)}

    def cleanup(self):
        """Clean up GPIO resources"""
        try:
            # Stop all PWM
            for pin in list(self.pwm_instances.keys()):
                self.stop_pwm_pin(pin)

            if GPIO_AVAILABLE:
                try:
                    GPIO.cleanup()
                    self.logger.info("GPIO cleanup completed")
                except Exception as e:
                    self.logger.warning(f"GPIO cleanup warning: {e}")
                finally:
                    self.gpio_initialized = False

            if self.pi and PIGPIO_AVAILABLE:
                try:
                    self.pi.stop()
                    self.pi = None  # Reset pi object after stopping
                    self.logger.info("pigpio cleanup completed")
                except Exception as e:
                    self.logger.warning(f"pigpio cleanup warning: {e}")
                    self.pi = None  # Ensure pi is None even if stop() fails

        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

    def get_pin_info(self, pin: int) -> Dict[str, Any]:
        """Get detailed information about a pin"""
        if pin in self.pin_states:
            pin_info = self.pin_states[pin].copy()
            pin_info["pin"] = pin
            pin_info["pwm_active"] = pin in self.pwm_instances
            if pin_info["pwm_active"]:
                pin_info["pwm_info"] = self.pwm_instances[pin]
            return pin_info
        else:
            return {"pin": pin, "configured": False, "message": "Pin not configured"}

    def get_system_status(self) -> Dict[str, Any]:
        """Get system status for debugging"""
        # Convert pin_states to JSON-serializable format
        serializable_pin_states = {}
        for pin, state in self.pin_states.items():
            serializable_pin_states[str(pin)] = {
                "mode": str(state.get("mode", "")),
                "state": (
                    int(state.get("state", 0))
                    if isinstance(state.get("state"), (int, bool))
                    else 0
                ),
                "pull_up_down": (
                    str(state.get("pull_up_down", ""))
                    if state.get("pull_up_down")
                    else None
                ),
            }

        # Check pigpio connection safely - return boolean only
        pigpio_connected = False
        if self.pi is not None:
            try:
                # Check if connected attribute exists and is True
                if hasattr(self.pi, "connected"):
                    connected_val = self.pi.connected
                    # Convert to bool (in case it's a Mock)
                    pigpio_connected = (
                        bool(connected_val) if not callable(connected_val) else True
                    )
                else:
                    # If no connected attribute, assume connected if pi object exists
                    pigpio_connected = True
            except Exception:
                pigpio_connected = False

        return {
            "gpio_available": bool(GPIO_AVAILABLE),
            "pigpio_available": bool(PIGPIO_AVAILABLE),
            "gpio_initialized": bool(self.gpio_initialized),
            "pigpio_connected": bool(pigpio_connected),
            "configured_pins": int(len(self.pin_states)),
            "active_pwm": int(len(self.pwm_instances)),
            "pin_states": serializable_pin_states,
        }
