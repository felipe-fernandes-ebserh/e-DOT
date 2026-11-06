"""
Testes de Segurança e RBAC: Usuários, Destinatários e Dependências de Autorização
================================================================================
Testa a lógica de atribuição de perfis, manutenção de destinatários e a validação
de autorização que bloqueia acessos não autorizados com HTTP 403 Forbidden.
"""

import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.resources.database import Base
from src.models.usuario import UsuarioSistema
from src.models.destinatario_notificacao import DestinatarioNotificacao
from src.controllers.usuario_controller import UsuarioController
from src.controllers.destinatario_controller import DestinatarioController
from src.dependencies import verify_coordenacao_or_admin


@pytest_asyncio.fixture
async def async_test_db():
    """Cria banco de dados assíncrono em memória SQLite para testes."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_usuario_controller_atribuir_perfil(async_test_db):
    """Testa atribuição de perfil com pré-validação mock no AD e gravação de auditoria."""
    # Usuário mockado do AD (ex: maria.souza)
    user = await UsuarioController.atribuir_perfil_usuario(
        db=async_test_db,
        username="maria.souza",
        perfil="COORDENACAO_CIHDOTT",
        operador="admin"
    )
    assert user.username == "maria.souza"
    assert user.perfil == "COORDENACAO_CIHDOTT"
    assert user.ativo is True

    # Alterar perfil para ADMINISTRADOR
    user_upd = await UsuarioController.atribuir_perfil_usuario(
        db=async_test_db,
        username="maria.souza",
        perfil="ADMINISTRADOR",
        operador="admin"
    )
    assert user_upd.perfil == "ADMINISTRADOR"

    # Perfil inválido deve disparar HTTP 400
    with pytest.raises(HTTPException) as exc:
        await UsuarioController.atribuir_perfil_usuario(
            db=async_test_db,
            username="maria.souza",
            perfil="PERFIL_INEXISTENTE",
            operador="admin"
        )
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_destinatario_controller_crud(async_test_db):
    """Testa ciclo completo de cadastro, atualização e exclusão de destinatários."""
    # Criação
    dest = await DestinatarioController.criar_destinatario(
        db=async_test_db,
        nome="Dra. Roberta",
        email_teams="roberta.medica@ebserh.gov.br",
        cargo_setor="Médica CIHDOTT",
        operador="coord.cihdott"
    )
    assert dest.id is not None
    assert dest.ativo is True

    # Duplicidade de e-mail deve disparar HTTP 409
    with pytest.raises(HTTPException) as exc:
        await DestinatarioController.criar_destinatario(
            db=async_test_db,
            nome="Outra Roberta",
            email_teams="roberta.medica@ebserh.gov.br",
            cargo_setor="Médica",
            operador="coord.cihdott"
        )
    assert exc.value.status_code == 409

    # Atualização
    dest_upd = await DestinatarioController.atualizar_destinatario(
        db=async_test_db,
        destinatario_id=dest.id,
        ativo=False,
        operador="coord.cihdott"
    )
    assert dest_upd.ativo is False

    # Remoção
    removido = await DestinatarioController.remover_destinatario(
        db=async_test_db,
        destinatario_id=dest.id,
        operador="coord.cihdott"
    )
    assert removido is True


@pytest.mark.asyncio
async def test_verify_coordenacao_or_admin_autorizacao(async_test_db):
    """Testa a regra de segurança RBAC: apenas admin e coordenação são aceitos; outros recebem 403."""
    # 1. Usuário com grupo AD mestre deve ser aprovado
    user_ad_admin = {"username": "qualquer.user", "groups": ["GLO-SEC-HCPE-SETISD"]}
    res = await verify_coordenacao_or_admin(current_user=user_ad_admin, db=async_test_db)
    assert res == user_ad_admin

    # 2. Usuário cadastrado localmente como COORDENACAO_CIHDOTT deve ser aprovado
    coord_user = UsuarioSistema(
        username="coord.teste",
        nome="Coordenador Teste",
        email="coord.teste@ebserh.gov.br",
        perfil="COORDENACAO_CIHDOTT",
        ativo=True
    )
    async_test_db.add(coord_user)
    await async_test_db.commit()

    res_coord = await verify_coordenacao_or_admin(
        current_user={"username": "coord.teste", "groups": []},
        db=async_test_db
    )
    assert res_coord["perfil"] == "COORDENACAO_CIHDOTT"

    # 3. Usuário cadastrado localmente com perfil CONSULTA deve ser bloqueado com 403
    consulta_user = UsuarioSistema(
        username="user.consulta",
        nome="Usuário Consulta",
        email="user.consulta@ebserh.gov.br",
        perfil="CONSULTA",
        ativo=True
    )
    async_test_db.add(consulta_user)
    await async_test_db.commit()

    with pytest.raises(HTTPException) as exc_consulta:
        await verify_coordenacao_or_admin(
            current_user={"username": "user.consulta", "groups": []},
            db=async_test_db
        )
    assert exc_consulta.value.status_code == 403

    # 4. Usuário não cadastrado localmente deve ser bloqueado com 403
    with pytest.raises(HTTPException) as exc_desconhecido:
        await verify_coordenacao_or_admin(
            current_user={"username": "desconhecido.ad", "groups": []},
            db=async_test_db
        )
    assert exc_desconhecido.value.status_code == 403
