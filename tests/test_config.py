"""
Test configuration
"""

import os
import pytest
from config import (
    Config,
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
    get_config,
)


class TestConfig:
    """Test configuration classes"""

    def test_base_config(self):
        """Test base configuration"""
        assert Config.HOST == "0.0.0.0"
        assert Config.PORT == 5000
        assert Config.DEBUG is False
        assert Config.TESTING is False

    def test_development_config(self):
        """Test development configuration"""
        assert DevelopmentConfig.DEBUG is True
        assert DevelopmentConfig.LOG_LEVEL == "DEBUG"

    def test_production_config(self):
        """Test production configuration"""
        assert ProductionConfig.DEBUG is False
        assert ProductionConfig.LOG_LEVEL == "INFO"

    def test_testing_config(self):
        """Test testing configuration"""
        assert TestingConfig.TESTING is True
        assert TestingConfig.DEBUG is True

    def test_get_config_default(self):
        """Test getting default configuration"""
        config = get_config()
        assert config == DevelopmentConfig

    def test_get_config_by_name(self):
        """Test getting configuration by name"""
        config = get_config("production")
        assert config == ProductionConfig

        config = get_config("development")
        assert config == DevelopmentConfig

        config = get_config("testing")
        assert config == TestingConfig

    def test_config_from_env(self):
        """Test configuration from environment variables"""
        os.environ["FLASK_ENV"] = "production"
        config = get_config()
        assert config == ProductionConfig

        # Cleanup
        del os.environ["FLASK_ENV"]

    def test_pwm_limits(self):
        """Test PWM safety limits"""
        assert Config.PWM_MAX_FREQUENCY == 50000
        assert Config.PWM_MIN_FREQUENCY == 1
        assert Config.PWM_MAX_DUTY_CYCLE == 100
        assert Config.PWM_MIN_DUTY_CYCLE == 0

    def test_cors_origins(self):
        """Test CORS origins configuration"""
        assert (
            "http://localhost:5000" in DevelopmentConfig.SOCKETIO_CORS_ALLOWED_ORIGINS
        )
        assert (
            "http://127.0.0.1:5000" in DevelopmentConfig.SOCKETIO_CORS_ALLOWED_ORIGINS
        )
