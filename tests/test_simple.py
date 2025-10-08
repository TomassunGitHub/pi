"""
Simple smoke tests to verify basic functionality
"""

import pytest


class TestBasicFunctionality:
    """Basic sanity tests"""

    def test_imports_work(self):
        """Test that basic imports work"""
        import sys

        assert "RPi" in sys.modules
        assert "RPi.GPIO" in sys.modules

    def test_app_creation(self, app):
        """Test that app is created successfully"""
        assert app is not None
        assert app.config["TESTING"] is True

    def test_client_works(self, client):
        """Test that test client works"""
        assert client is not None

    def test_simple_math(self):
        """Simplest possible test"""
        assert 1 + 1 == 2
        assert True is True

    def test_dict_operations(self):
        """Test basic dict operations"""
        data = {"pin": 17, "state": 1}
        assert data["pin"] == 17
        assert data["state"] == 1

    def test_list_operations(self):
        """Test basic list operations"""
        pins = [17, 18, 22]
        assert len(pins) == 3
        assert 17 in pins
