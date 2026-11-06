import pytest
from unittest.mock import AsyncMock, patch
from starlette.testclient import TestClient

def get_admin_token(client: TestClient) -> str:
    res = client.post("/api/login", data={"username": "admin", "password": "admin"})
    assert res.status_code == 200
    return res.json()["access_token"]

def test_csh_endpoints(client: TestClient):
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Teste de conexão CSH
    with patch("src.providers.implementations.obito_mysql_provider.ObitoMySqlProvider.testar_conexao", new_callable=AsyncMock) as mock_test:
        mock_test.return_value = {"status": "sucesso", "resultado": 1}
        with patch("src.providers.implementations.obito_mysql_provider.ObitoMySqlProvider.buscar_obitos_pendentes", new_callable=AsyncMock) as mock_busca:
            mock_busca.return_value = [{"id_evento_origem": "176", "id_chamado_material": 176}]
            
            resp = client.get("/api/notificacoes/csh/teste-conexao", headers=headers)
            assert resp.status_code == 200
            data = resp.json()
            assert data["diagnostico"]["status"] == "sucesso"
            assert data["total_amostra"] == 1

    # 2. Teste de sincronização CSH
    with patch("src.controllers.notificacao_obito_controller.NotificacaoObitoController.sincronizar_obitos_csh", new_callable=AsyncMock) as mock_sync:
        mock_sync.return_value = {
            "total_encontrados": 1,
            "novos_notificados": 1,
            "ignorados_duplicados": 0,
            "falhas": 0,
            "detalhes": [{"id_chamado": "176", "status": "ENVIADO"}]
        }
        resp_sync = client.post("/api/notificacoes/csh/sincronizar?limite=10", headers=headers)
        assert resp_sync.status_code == 200
        data_sync = resp_sync.json()
        assert data_sync["total_encontrados"] == 1
        assert data_sync["novos_notificados"] == 1
