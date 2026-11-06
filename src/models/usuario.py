"""
Modelo SQLAlchemy de Usuários e Perfis de Acesso Locais (RBAC)
=============================================================
Gerencia os usuários autorizados na aplicação, vinculando a identidade corporativa do AD
(username) aos perfis locais (ADMINISTRADOR, COORDENACAO_CIHDOTT, EQUIPE_BUSCA_ATIVA, CONSULTA).
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from ..resources.database import Base


class UsuarioSistema(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    nome = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    departamento = Column(String(100), nullable=True)
    perfil = Column(String(50), nullable=False, default="CONSULTA")  # ADMINISTRADOR, COORDENACAO_CIHDOTT, EQUIPE_BUSCA_ATIVA, CONSULTA
    ativo = Column(Boolean, default=True, nullable=False)
    data_criacao = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    data_atualizacao = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<UsuarioSistema username={self.username} perfil={self.perfil} ativo={self.ativo}>"
