# tests/conftest.py
import pytest
import os
import sys

# Ensure src directory is in sys.path for test imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from src.main import app
from src.auth.auth import auth_handler, MockAuthProvider

from unittest.mock import patch

@pytest.fixture(autouse=True)
def configure_test_auth():
    """Garante que a suíte de testes utilize MockAuthProvider."""
    original_provider = auth_handler.provider
    auth_handler.provider = MockAuthProvider()
    yield
    auth_handler.provider = original_provider

@pytest.fixture(autouse=True)
def mock_teams_webhook(request):
    """Garante que a suíte de testes não dispare chamadas HTTP reais para o Teams fora de test_teams_service."""
    if "test_teams_service" in request.node.name or "test_teams_service.py" in str(getattr(request.node, "fspath", "")):
        yield
        return

    with patch("src.services.teams_service.TeamsService.send_notification") as mock_send:
        mock_send.return_value = {
            "success": True,
            "simulated": True,
            "status_code": 200,
            "attempts": 1,
            "error": None
        }
        yield mock_send

@pytest.fixture
def client():
    """
    Fixture de teste que fornece um TestClient configurado para fazer requisições à aplicação FastAPI.
    """
    with TestClient(app) as test_client:
        yield test_client

