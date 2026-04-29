"""
Tests de integración para la API.
"""

import pytest
from fastapi.testclient import TestClient

from kronos.infrastructure.api import app


@pytest.fixture
def client():
    """Cliente de prueba para la API."""
    return TestClient(app)


class TestHealthEndpoints:
    """Tests para endpoints de salud."""

    def test_health_endpoint(self, client):
        """Endpoint /health debe retornar status healthy."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Endpoint raíz debe retornar información de la API."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


class TestDecisionsEndpoints:
    """Tests para endpoints de decisiones."""

    def test_get_decision_with_coordinates(self, client):
        """GET /decisions debe funcionar con coordenadas."""
        response = client.get(
            "/api/v1/decisions",
            params={"lat": 19.0425, "lng": -98.1981, "speed": 13.89},
        )
        assert response.status_code == 200
        data = response.json()
        assert "decision" in data
        assert "risk_score" in data
        assert "message" in data
        assert "position" in data

    def test_get_decision_with_osm(self, client):
        """GET /decisions debe funcionar con use_osm."""
        response = client.get(
            "/api/v1/decisions",
            params={
                "lat": 19.0425,
                "lng": -98.1981,
                "speed": 13.89,
                "use_osm": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "decision" in data

    def test_post_decision_with_destination(self, client):
        """POST /decisions debe funcionar con destino."""
        response = client.post(
            "/api/v1/decisions",
            json={
                "lat": 19.0425,
                "lng": -98.1981,
                "speed": 13.89,
                "destination_lat": 19.0500,
                "destination_lng": -98.2267,
                "use_osm": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "decision" in data
        assert "position" in data

    def test_decision_without_coordinates(self, client):
        """GET /decisions sin coordenadas debe usar valores por defecto."""
        response = client.get("/api/v1/decisions")
        assert response.status_code == 200
        data = response.json()
        assert "decision" in data


class TestVoiceEndpoints:
    """Tests para endpoints de voz."""

    def test_welcome_message(self, client):
        """GET /welcome/message debe retornar mensaje."""
        response = client.get("/api/v1/welcome/message")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_welcome_audio(self, client):
        """GET /welcome/audio debe retornar audio MP3."""
        response = client.get("/api/v1/welcome/audio")
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"

    def test_text_to_speech(self, client):
        """GET /audio/text debe convertir texto a voz."""
        response = client.get(
            "/api/v1/audio/text", params={"text": "Prueba de voz"}
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"

    def test_decision_audio(self, client):
        """GET /audio debe retornar audio de decisión."""
        response = client.get(
            "/api/v1/audio",
            params={"lat": 19.0425, "lng": -98.1981, "speed": 13.89},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
