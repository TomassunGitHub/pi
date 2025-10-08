"""
Configuration management for Raspberry Pi GPIO Control Application
"""

import os
from typing import Dict, Any


class Config:
    """Base configuration"""

    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32).hex())

    # Server settings
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 5000))

    # SocketIO settings
    # For local network use, allow localhost and local IPs
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5000,http://127.0.0.1:5000,http://raspberrypi.local:5000",
    ).split(",")
    SOCKETIO_ASYNC_MODE = "eventlet"

    # GPIO settings
    GPIO_MODE = "BCM"  # BCM or BOARD numbering
    GPIO_WARNINGS = False

    # PWM limits (hardware safety)
    PWM_MAX_FREQUENCY = 50000  # 50kHz maximum
    PWM_MIN_FREQUENCY = 1  # 1Hz minimum
    PWM_MAX_DUTY_CYCLE = 100
    PWM_MIN_DUTY_CYCLE = 0

    # Logging settings
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    # Application settings
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    LOG_LEVEL = "DEBUG"
    # In development, allow all local origins
    SOCKETIO_CORS_ALLOWED_ORIGINS = [
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://raspberrypi.local:5000",
    ]


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    LOG_LEVEL = "INFO"
    # In production, be more restrictive
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get(
        "CORS_ALLOWED_ORIGINS", "http://raspberrypi.local:5000"
    ).split(",")


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    DEBUG = True
    LOG_LEVEL = "DEBUG"


# Configuration dictionary
config_by_name: Dict[str, Any] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config(config_name: str = None) -> Config:
    """Get configuration by name"""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")
    return config_by_name.get(config_name, DevelopmentConfig)
