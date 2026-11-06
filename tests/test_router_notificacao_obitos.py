"""
Testes de Integração da API de Notificações de Óbito e Teams (e-DOT)
===================================================================
Testa endpoints HTTP: autenticação, autorização, CRUD de destinatários,
disparo de teste para o Teams (Modo Completo vs Simples) e histórico.
"""

import pytest
from fastapi.testclient import TestClient


def get_admin_token(client: TestClient) -> str:
    """Obtém token JWT para o usuário mock admin."""
    res = client.post("/api/login", data={"username": "admin", "password": "admin"})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_rotas_protegidas_sem_token(client: TestClient):
    """Garante que requisições sem token JWT sejam rejeitadas com 401 Unauthorized."""
    assert client.get("/api/notificacoes/destinatarios").status_code == 401
    assert client.post("/api/notificacoes/teste-teams", json={"modo": "COMPLETO"}).status_code == 401
    assert client.get("/api/notificacoes/obitos").status_code == 401
    assert client.get("/api/usuarios").status_code == 401


import uuid

def test_crud_destinatarios_api(client: TestClient):
    """Testa cadastro e listagem de destinatários do Teams via API autenticada."""
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    unique_email = f"plantonista.{uuid.uuid4().hex[:6]}@ebserh.gov.br"

    # 1. Cadastra destinatário
    payload_dest = {
        "nome": "Plantonista CIHDOTT Teste",
        "email_teams": unique_email,
        "cargo_setor": "Médico CIHDOTT"
    }
    res_create = client.post("/api/notificacoes/destinatarios", json=payload_dest, headers=headers)
    assert res_create.status_code == 201
    dest_data = res_create.json()
    assert dest_data["nome"] == "Plantonista CIHDOTT Teste"
    dest_id = dest_data["id"]

    # 2. Lista destinatários
    res_list = client.get("/api/notificacoes/destinatarios", headers=headers)
    assert res_list.status_code == 200
    dest_list = res_list.json()
    assert any(d["id"] == dest_id for d in dest_list)

    # 3. Atualiza destinatário (inativação)
    res_upd = client.put(f"/api/notificacoes/destinatarios/{dest_id}", json={"ativo": False}, headers=headers)
    assert res_upd.status_code == 200
    assert res_upd.json()["ativo"] is False

    # 4. Reativação
    res_reactivate = client.put(f"/api/notificacoes/destinatarios/{dest_id}", json={"ativo": True}, headers=headers)
    assert res_reactivate.status_code == 200
    assert res_reactivate.json()["ativo"] is True

    # 5. Limpeza: remove o registro de teste para não poluir o banco local
    res_del = client.delete(f"/api/notificacoes/destinatarios/{dest_id}", headers=headers)
    assert res_del.status_code == 200


def test_disparo_teste_teams_modo_completo_e_simples(client: TestClient):
    """Testa endpoints de disparo simulado no Teams em Modo Completo e Modo Alerta Simples."""
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Disparo de teste em Modo Completo
    res_completo = client.post("/api/notificacoes/teste-teams", json={"modo": "COMPLETO"}, headers=headers)
    assert res_completo.status_code == 200
    data_comp = res_completo.json()
    assert data_comp["modo_apresentacao"] == "COMPLETO"
    assert data_comp["status_envio"] in ("SIMULADO", "ENVIADO")
    assert "Paciente Simulado" in (data_comp["nome_paciente"] or "")

    # 2. Disparo de teste em Modo Alerta Simples
    res_simples = client.post("/api/notificacoes/teste-teams", json={"modo": "ALERTA_SIMPLES"}, headers=headers)
    assert res_simples.status_code == 200
    data_simp = res_simples.json()
    assert data_simp["modo_apresentacao"] == "ALERTA_SIMPLES"
    assert data_simp["status_envio"] in ("SIMULADO", "ENVIADO")
    assert data_simp["nome_paciente"] is None

    # 3. Disparo de teste com dados customizados
    payload_custom = {
        "modo": "COMPLETO",
        "dados_obito": {
            "nome_paciente": "Maria da Silva Customizada",
            "setor_leito": "Bloco Cirúrgico - Sala 3",
            "prontuario": "PRONT-998877"
        }
    }
    res_custom = client.post("/api/notificacoes/teste-teams", json=payload_custom, headers=headers)
    assert res_custom.status_code == 200
    data_cust = res_custom.json()
    assert data_cust["nome_paciente"] == "Maria da Silva Customizada"
    assert data_cust["setor_leito"] == "Bloco Cirúrgico - Sala 3"
    assert data_cust["prontuario"] == "PRONT-998877"

    # 4. Disparo em Modo Apenas Simulação (Sem chamada externa ao Teams)
    payload_simulado = {
        "modo": "ALERTA_SIMPLES",
        "apenas_simular": True,
        "notificar_apenas_operador": True
    }
    res_sim = client.post("/api/notificacoes/teste-teams", json=payload_simulado, headers=headers)
    assert res_sim.status_code == 200
    assert res_sim.json()["status_envio"] == "SIMULADO"

    # 5. Disparo com lista vazia de destinatários (Sem @menções no cartão)
    payload_sem_mencoes = {
        "modo": "ALERTA_SIMPLES",
        "apenas_simular": True,
        "destinatarios_ids": []
    }
    res_sem = client.post("/api/notificacoes/teste-teams", json=payload_sem_mencoes, headers=headers)
    assert res_sem.status_code == 200
    assert res_sem.json()["status_envio"] == "SIMULADO"



def test_registro_obito_e_idempotencia_api(client: TestClient):
    """Testa registro de óbito de contingência e garantia de idempotência via API."""
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    payload_obito = {
        "fonte_origem": "CONTINGENCIA",
        "id_evento_origem": "CONTING-API-999",
        "nome_paciente": "Dona Antônia Pereira",
        "idade": 61,
        "setor_leito": "UTI Pediátrica/Adulto - Leito 01",
        "causa_morte": "Falência Múltipla de Órgãos",
        "prontuario": None  # Teste de tolerância a prontuário ausente
    }

    # Primeiro envio
    res1 = client.post("/api/notificacoes/obitos", json=payload_obito, headers=headers)
    assert res1.status_code == 200
    notif1 = res1.json()
    assert notif1["id_evento_origem"] == "CONTING-API-999"

    # Segundo envio idêntico (idempotência): não cria nova, retorna a mesma
    res2 = client.post("/api/notificacoes/obitos", json=payload_obito, headers=headers)
    assert res2.status_code == 200
    notif2 = res2.json()
    assert notif2["id"] == notif1["id"]

    # Histórico de notificações
    res_hist = client.get("/api/notificacoes/obitos", headers=headers)
    assert res_hist.status_code == 200
    assert len(res_hist.json()) >= 1


def test_gestao_usuarios_rbac_api(client: TestClient):
    """Testa atribuição de perfis de usuário via API autenticada."""
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Atribui perfil COORDENACAO_CIHDOTT ao usuário mock joao.silva
    res_perfil = client.post(
        "/api/usuarios/joao.silva/perfil",
        json={"perfil": "COORDENACAO_CIHDOTT"},
        headers=headers
    )
    assert res_perfil.status_code == 200
    user_data = res_perfil.json()
    assert user_data["username"] == "joao.silva"
    assert user_data["perfil"] == "COORDENACAO_CIHDOTT"

    # Lista usuários
    res_list = client.get("/api/usuarios", headers=headers)
    assert res_list.status_code == 200
    users = res_list.json()
    assert any(u["username"] == "joao.silva" for u in users)
