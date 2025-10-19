from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import logging
import os
from functools import wraps
from config import get_config


def socketio_error_handler(f):
    """Decorator for handling errors in SocketIO event handlers"""

    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            try:
                emit(
                    "gpio_response",
                    {
                        "success": False,
                        "error": f"Server error: {str(e)}",
                        "handler": f.__name__,
                    },
                )
            except Exception as emit_error:
                # If emit fails (e.g., no request context), just log it
                logger.debug(f"Could not emit error response: {emit_error}")

    return wrapped


def create_app(config_name=None):
    app = Flask(__name__)

    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize SocketIO with configuration
    socketio = SocketIO(
        app,
        cors_allowed_origins=config.SOCKETIO_CORS_ALLOWED_ORIGINS,
        async_mode=config.SOCKETIO_ASYNC_MODE,
    )

    # Configure logging with config settings
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        datefmt=config.LOG_DATE_FORMAT,
    )
    logger = logging.getLogger(__name__)

    # Import GPIO controller
    from .gpio_controller import GPIOController
    from .demos import SG90Servo

    gpio_controller = GPIOController(socketio)

    # Initialize demo components
    servo = SG90Servo(pin=18)  # GPIO 18 supports hardware PWM

    # Routes
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/status")
    def status():
        return {"status": "ok", "message": "Raspberry Pi 3 Application Running"}

    @app.route("/debug")
    def debug():
        """Debug endpoint to check GPIO system status"""
        try:
            system_status = gpio_controller.get_system_status()
            return {"status": "ok", "debug_info": system_status}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # Demo routes
    @app.route("/demos/servo-sg90")
    def demo_servo_sg90():
        """SG90 Servo demo page"""
        return render_template("demos/servo_sg90.html")

    # SocketIO events
    @socketio.on("connect")
    def handle_connect():
        logger.info("Client connected")
        emit("status", {"connected": True})

    @socketio.on("disconnect")
    def handle_disconnect():
        logger.info("Client disconnected")

    @socketio.on("gpio_set_mode")
    @socketio_error_handler
    def handle_gpio_set_mode(data):
        """Set GPIO pin mode (input/output/input_pullup/input_pulldown)"""
        pin = data.get("pin")
        mode = data.get("mode")
        logger.info(f"Received gpio_set_mode request: pin={pin}, mode={mode}")
        if pin is not None and mode:
            logger.info(f"Calling set_pin_mode...")
            result = gpio_controller.set_pin_mode(pin, mode)
            logger.info(f"set_pin_mode returned: {result}")
            logger.info(f"About to emit response...")
            try:
                emit("gpio_response", result)
                logger.info(f"emit successful")
            except Exception as e:
                logger.error(f"emit failed: {type(e).__name__}: {e}", exc_info=True)
                raise
        else:
            emit(
                "gpio_response",
                {"success": False, "error": "Missing pin or mode parameter"},
            )

    @socketio.on("gpio_write")
    @socketio_error_handler
    def handle_gpio_write(data):
        """Write value to GPIO pin"""
        pin = data.get("pin")
        value = data.get("value")
        if pin is not None and value is not None:
            result = gpio_controller.write_pin(pin, int(value))
            emit("gpio_response", result)
        else:
            emit(
                "gpio_response",
                {"success": False, "error": "Missing pin or value parameter"},
            )

    @socketio.on("gpio_toggle")
    @socketio_error_handler
    def handle_gpio_toggle(data):
        """Toggle GPIO pin output"""
        pin = data.get("pin")
        if pin:
            result = gpio_controller.toggle_pin(pin)
            emit("gpio_response", result)

    @socketio.on("gpio_read")
    @socketio_error_handler
    def handle_gpio_read(data):
        """Read GPIO pin state"""
        pin = data.get("pin")
        if pin:
            result = gpio_controller.read_pin(pin)
            emit("gpio_response", result)

    @socketio.on("gpio_read_all")
    @socketio_error_handler
    def handle_gpio_read_all():
        """Read all configured GPIO pins"""
        result = gpio_controller.read_all_pins()
        emit("gpio_response", result)

    @socketio.on("pwm_start")
    @socketio_error_handler
    def handle_pwm_start(data):
        """Start PWM on a pin"""
        pin = data.get("pin")
        frequency = data.get("frequency", 1000)
        duty_cycle = data.get("duty_cycle", 50)

        if pin is not None:
            result = gpio_controller.start_pwm(pin, frequency, duty_cycle)
            emit("gpio_response", result)
        else:
            emit("gpio_response", {"success": False, "error": "Missing pin parameter"})

    @socketio.on("pwm_stop")
    @socketio_error_handler
    def handle_pwm_stop(data):
        """Stop PWM on a pin"""
        pin = data.get("pin")
        if pin is not None:
            result = gpio_controller.stop_pwm(pin)
            emit("gpio_response", result)
        else:
            emit("gpio_response", {"success": False, "error": "Missing pin parameter"})

    @socketio.on("gpio_reset_all")
    @socketio_error_handler
    def handle_gpio_reset_all():
        """Reset all GPIO pins"""
        result = gpio_controller.reset_all_pins()
        emit("gpio_response", result)

    @socketio.on("gpio_cleanup")
    @socketio_error_handler
    def handle_gpio_cleanup():
        """Clean up all GPIO resources"""
        gpio_controller.cleanup()
        emit("gpio_response", {"success": True, "message": "GPIO cleanup completed"})

    @socketio.on("get_pin_info")
    @socketio_error_handler
    def handle_get_pin_info(data):
        """Get detailed information about a pin"""
        pin = data.get("pin")
        if pin is not None:
            result = gpio_controller.get_pin_info(pin)
            emit("pin_info_response", result)
        else:
            emit(
                "pin_info_response",
                {"success": False, "error": "Missing pin parameter"},
            )

    # ========================
    # Servo Demo SocketIO Events
    # ========================

    @socketio.on("servo_enable")
    @socketio_error_handler
    def handle_servo_enable():
        """Enable servo motor"""
        result = servo.enable()
        emit("servo_response", result)
        if result["success"]:
            # Emit initial status
            status = servo.get_status()
            emit("servo_status", status)

    @socketio.on("servo_disable")
    @socketio_error_handler
    def handle_servo_disable():
        """Disable servo motor"""
        result = servo.disable()
        emit("servo_response", result)
        if result["success"]:
            status = servo.get_status()
            emit("servo_status", status)

    @socketio.on("servo_set_angle")
    @socketio_error_handler
    def handle_servo_set_angle(data):
        """Set servo angle"""
        angle = data.get("angle")
        smooth = data.get("smooth", False)

        if angle is not None:
            result = servo.set_angle(angle, smooth)
            emit("servo_response", result)
            if result["success"]:
                status = servo.get_status()
                emit("servo_status", status)
        else:
            emit(
                "servo_response", {"success": False, "error": "Missing angle parameter"}
            )

    @socketio.on("servo_step")
    @socketio_error_handler
    def handle_servo_step(data):
        """Step move servo"""
        step = data.get("step")

        if step is not None:
            result = servo.step_move(step)
            emit("servo_response", result)
            if result["success"]:
                status = servo.get_status()
                emit("servo_status", status)
        else:
            emit(
                "servo_response", {"success": False, "error": "Missing step parameter"}
            )

    @socketio.on("servo_scan_start")
    @socketio_error_handler
    def handle_servo_scan_start(data):
        """Start servo scan mode"""
        start_angle = data.get("start_angle", 0)
        end_angle = data.get("end_angle", 180)
        speed = data.get("speed", "medium")

        result = servo.start_scan(start_angle, end_angle, speed)
        emit("servo_response", result)
        if result["success"]:
            status = servo.get_status()
            emit("servo_status", status)

    @socketio.on("servo_scan_stop")
    @socketio_error_handler
    def handle_servo_scan_stop():
        """Stop servo scan mode"""
        result = servo.stop_scan()
        emit("servo_response", result)
        if result["success"]:
            status = servo.get_status()
            emit("servo_status", status)

    @socketio.on("servo_emergency_stop")
    @socketio_error_handler
    def handle_servo_emergency_stop():
        """Emergency stop servo"""
        result = servo.emergency_stop()
        emit("servo_response", result)
        status = servo.get_status()
        emit("servo_status", status)

    @socketio.on("servo_get_status")
    @socketio_error_handler
    def handle_servo_get_status():
        """Get servo status"""
        status = servo.get_status()
        emit("servo_status", status)

    # Note: GPIO cleanup is handled via:
    # 1. User clicking "清理GPIO" button (socketio event: gpio_cleanup)
    # 2. Application shutdown signal handlers (in run.py)
    # We do NOT use @app.teardown_appcontext as it runs after EVERY request,
    # which would destroy GPIO state between operations!

    return app, socketio
