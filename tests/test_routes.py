"""
Test HTTP routes
"""

import pytest


class TestRoutes:
    """Test HTTP endpoint routes"""

    def test_index_page(self, client):
        """Test the main index page loads"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"GPIO" in response.data or b"gpio" in response.data

    def test_status_endpoint(self, client):
        """Test the status endpoint"""
        response = client.get("/status")
        assert response.status_code == 200

        data = response.get_json()
        assert data["status"] == "ok"
        assert "message" in data

    def test_debug_endpoint(self, client):
        """Test the debug endpoint"""
        response = client.get("/debug")
        assert response.status_code == 200

        # Check that response is JSON
        assert response.content_type == "application/json"

        data = response.get_json()
        assert "status" in data

        # Debug endpoint may return error or ok, both are valid
        assert data["status"] in ["ok", "error"]

    def test_404_error(self, client):
        """Test 404 error for non-existent route"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
