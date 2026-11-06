"""
Modelo SQLAlchemy de Destinatários da Notificação (Microsoft Teams)
===================================================================
Gerencia os membros da equipe de busca ativa (CIHDOTT) que receberão
as @menções individuais nos alertas enviados ao canal do Teams.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from ..resources.database import Base


class DestinatarioNotificacao(Base):
    __tablename__ = "destinatarios_notificacao"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    email_teams = Column(String(150), unique=True, nullable=False, index=True)
    cargo_setor = Column(String(100), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    data_criacao = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    data_atualizacao = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<DestinatarioNotificacao nome={self.nome} email={self.email_teams} ativo={self.ativo}>"
