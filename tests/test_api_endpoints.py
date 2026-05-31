import pytest
from litestar.status_codes import HTTP_200_OK
from litestar.testing import TestClient
from src.api.app import app

def test_health_endpoint():
    """Verify that the health check endpoint returns a 200 OK status."""
    with TestClient(app=app) as client:
        response = client.get("/health")
        assert response.status_code == HTTP_200_OK
        assert response.json() == {"status": "ok"}

def test_stats_endpoint():
    """Verify that the stats endpoint returns the correct service structure."""
    with TestClient(app=app) as client:
        response = client.get("/stats")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert "services" in data
        assert "web" in data["services"]
        assert "bot" in data["services"]
        assert "poller" in data["services"]
        assert data["services"]["web"]["status"] == "operational"
        assert "timestamp" in data
