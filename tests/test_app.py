from fastapi.testclient import TestClient

from src.app.main import app


def test_app_wires_up_expected_routes():
    with TestClient(app) as client:
        paths = {route.path for route in app.routes}
        assert "/retail-insights-agent" in paths
        assert "/retail-insights-agent/health" in paths
        assert "/retail-insights-agent/threads/{thread_id}/state" in paths

        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["environment"] == "test"
