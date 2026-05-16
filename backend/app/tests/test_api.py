"""Basic API endpoint tests."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test that OpenAPI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema(client: TestClient):
    """Test that OpenAPI schema endpoint works."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()
