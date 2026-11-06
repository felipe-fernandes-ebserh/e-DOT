"""
Testes Unitários do Serviço e Helper do Microsoft Teams (Adaptive Cards e Envio)
================================================================================
Testa a montagem de Adaptive Cards (Modo Completo vs Modo Simples), @menções individuais,
modo simulado (Mock) e política de retentativas HTTP.
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

from src.helpers.teams_card_helper import build_teams_adaptive_card
from src.services.teams_service import TeamsService


def test_build_teams_card_modo_completo_com_mencoes():
    """Valida a geração do cartão adaptativo em Modo Completo com @menções nominais."""
    dados_obito = {
        "nome_paciente": "Dona Francisca Maria",
        "idade": 68,
        "causa_morte": "Hemorragia Subaracnóidea",
        "setor_leito": "UTI Geral - Leito 05",
        "prontuario": "987654"
    }
    destinatarios = [
        {"nome": "Ana Paula", "email_teams": "ana.paula@ebserh.gov.br"},
        {"nome": "Carlos Silva", "email_teams": "carlos.silva@ebserh.gov.br"}
    ]
    
    payload = build_teams_adaptive_card(dados_obito, destinatarios)
    
    assert payload["type"] == "message"
    card = payload["attachments"][0]["content"]
    assert card["type"] == "AdaptiveCard"
    
    # Verifica título do modo completo
    textos = [elem.get("text", "") for elem in card["body"] if elem.get("type") == "TextBlock"]
    assert any("ALERTA DE ÓBITO — BUSCA ATIVA" in t for t in textos)
    assert any("<at>Ana Paula</at>" in t for t in textos)
    
    # Verifica entidades msteams
    entities = card.get("msteams", {}).get("entities", [])
    assert len(entities) == 2
    assert entities[0]["mentioned"]["id"] == "ana.paula@ebserh.gov.br"
    assert entities[1]["mentioned"]["id"] == "carlos.silva@ebserh.gov.br"
    
    # Verifica fatos
    fact_set = next(elem for elem in card["body"] if elem.get("type") == "FactSet")
    facts_dict = {f["title"]: f["value"] for f in fact_set["facts"]}
    assert facts_dict["Paciente:"] == "Dona Francisca Maria"
    assert facts_dict["Prontuário:"] == "987654"


def test_build_teams_card_modo_simples_e_prontuario_pendente():
    """Valida geração do cartão em Modo Alerta Simples (sem paciente definido)."""
    dados_obito = {
        "nome_paciente": None,
        "setor_leito": "Enfermaria 3 Sul - Leito 312",
        "causa_morte": None,
        "prontuario": None
    }
    destinatarios = [{"nome": "Equipe Plantão", "email_teams": "plantao@ebserh.gov.br"}]
    
    payload = build_teams_adaptive_card(dados_obito, destinatarios)
    card = payload["attachments"][0]["content"]
    
    textos = [elem.get("text", "") for elem in card["body"] if elem.get("type") == "TextBlock"]
    assert any("ALERTA DE ÓBITO HOSPITALAR" in t for t in textos)
    assert any("Iniciar busca ativa presencial" in t for t in textos)
    
    entities = card.get("msteams", {}).get("entities", [])
    assert len(entities) == 1
    assert entities[0]["mentioned"]["id"] == "plantao@ebserh.gov.br"


@pytest.mark.asyncio
async def test_teams_service_modo_simulado():
    """Valida que o serviço opera em Modo Mock quando a URL do webhook não está configurada."""
    service = TeamsService(webhook_url="")
    payload = {"type": "message", "attachments": []}
    
    res = await service.send_notification(payload)
    assert res["success"] is True
    assert res["simulated"] is True
    assert res["status_code"] == 200
    assert res["attempts"] == 1


@pytest.mark.asyncio
async def test_teams_service_envio_com_sucesso():
    """Valida o envio bem-sucedido mockando a resposta HTTP da API do Teams."""
    service = TeamsService(webhook_url="https://webhook.teams.office.com/teste/valido", max_retries=2)
    payload = {"type": "message", "attachments": []}
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        res = await service.send_notification(payload)
        
        assert res["success"] is True
        assert res["simulated"] is False
        assert res["status_code"] == 200
        assert res["attempts"] == 1
        assert mock_post.await_count == 1


@pytest.mark.asyncio
async def test_teams_service_falha_com_retentativas():
    """Valida que o serviço esgota as retentativas em caso de erro 500 e reporta falha."""
    service = TeamsService(webhook_url="https://webhook.teams.office.com/teste/valido", max_retries=2)
    payload = {"type": "message", "attachments": []}
    
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        res = await service.send_notification(payload)
        
        assert res["success"] is False
        assert res["simulated"] is False
        assert res["status_code"] == 500
        assert res["attempts"] == 2
        assert "Erro HTTP 500" in res["error"]
        assert mock_post.await_count == 2
