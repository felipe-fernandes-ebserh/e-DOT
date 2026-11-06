"""
Testes Unitários dos Modelos de Notificação e Usuários (e-DOT)
==============================================================
Valida a integridade dos modelos SQLAlchemy, valores padrão e constraints de unicidade
para UsuarioSistema, DestinatarioNotificacao e NotificacaoObito.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from src.resources.database import Base
from src.models.usuario import UsuarioSistema
from src.models.destinatario_notificacao import DestinatarioNotificacao
from src.models.notificacao_obito import NotificacaoObito


@pytest.fixture
def sync_db_session():
    """Cria banco SQLite em memória para testar modelos de forma isolada e síncrona."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


def test_usuario_sistema_model(sync_db_session):
    """Testa criação e valores padrão do modelo UsuarioSistema."""
    user = UsuarioSistema(
        username="ana.paula",
        nome="Ana Paula Silva",
        email="ana.paula@ebserh.gov.br",
        perfil="COORDENACAO_CIHDOTT"
    )
    sync_db_session.add(user)
    sync_db_session.commit()

    assert user.id is not None
    assert user.ativo is True
    assert user.perfil == "COORDENACAO_CIHDOTT"
    assert "Ana Paula" in repr(user) or "ana.paula" in repr(user)

    # Teste de unicidade de username
    duplicate_user = UsuarioSistema(
        username="ana.paula",
        nome="Outra Ana",
        email="outra.ana@ebserh.gov.br"
    )
    sync_db_session.add(duplicate_user)
    with pytest.raises(IntegrityError):
        sync_db_session.commit()
    sync_db_session.rollback()


def test_destinatario_notificacao_model(sync_db_session):
    """Testa criação e constraint de unicidade do e-mail do Teams."""
    dest = DestinatarioNotificacao(
        nome="Carlos Eduardo",
        email_teams="carlos.eduardo@ebserh.gov.br",
        cargo_setor="Enfermeiro CIHDOTT"
    )
    sync_db_session.add(dest)
    sync_db_session.commit()

    assert dest.id is not None
    assert dest.ativo is True

    # Teste de unicidade do email_teams
    dup_dest = DestinatarioNotificacao(
        nome="Carlos Clone",
        email_teams="carlos.eduardo@ebserh.gov.br"
    )
    sync_db_session.add(dup_dest)
    with pytest.raises(IntegrityError):
        sync_db_session.commit()
    sync_db_session.rollback()


def test_notificacao_obito_model_e_idempotencia(sync_db_session):
    """Testa criação, campos opcionais e constraint única composta para idempotência."""
    notif = NotificacaoObito(
        fonte_origem="CSH_MYSQL",
        id_evento_origem="OBT-2026-001",
        nome_paciente="Severino do Carmo",
        idade=72,
        setor_leito="UTI Coronariana - Leito 03",
        status_envio="PENDENTE"
    )
    sync_db_session.add(notif)
    sync_db_session.commit()

    assert notif.id is not None
    assert notif.modo_apresentacao == "COMPLETO"
    assert notif.tentativas_envio == 0
    assert notif.prontuario is None  # Tolerância à ausência de prontuário

    # Teste de duplicidade: mesma fonte_origem e id_evento_origem deve falhar
    notif_dup = NotificacaoObito(
        fonte_origem="CSH_MYSQL",
        id_evento_origem="OBT-2026-001",
        nome_paciente="Severino Repetido"
    )
    sync_db_session.add(notif_dup)
    with pytest.raises(IntegrityError):
        sync_db_session.commit()
    sync_db_session.rollback()

    # Outra fonte_origem com mesmo id_evento_origem deve ser aceita
    notif_outra_fonte = NotificacaoObito(
        fonte_origem="CONTINGENCIA",
        id_evento_origem="OBT-2026-001",
        nome_paciente="Outro Paciente"
    )
    sync_db_session.add(notif_outra_fonte)
    sync_db_session.commit()
    assert notif_outra_fonte.id is not None
