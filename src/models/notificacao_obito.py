"""
Modelo SQLAlchemy de Histórico de Notificações de Óbito (Idempotência e Rastreabilidade)
========================================================================================
Armazena todos os eventos de óbito recebidos e processados, garantindo idempotência
estrita através de chave única composta (fonte_origem + id_evento_origem) e rastreando
o status de envio e os destinatários marcados no Microsoft Teams.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from ..resources.database import Base


class NotificacaoObito(Base):
    __tablename__ = "notificacoes_obitos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fonte_origem = Column(String(50), nullable=False, default="CSH_MYSQL")  # CSH_MYSQL, CONTINGENCIA, TESTE
    id_evento_origem = Column(String(100), nullable=False, index=True)
    
    # Dados clínicos (toleram ausência no Modo Alerta Simples)
    nome_paciente = Column(String(150), nullable=True)
    idade = Column(Integer, nullable=True)
    sexo = Column(String(20), nullable=True)
    causa_morte = Column(Text, nullable=True)
    setor_leito = Column(String(100), nullable=True)
    prontuario = Column(String(50), nullable=True)
    data_hora_obito = Column(DateTime, nullable=True)
    
    # Modo de apresentação e envio
    modo_apresentacao = Column(String(50), default="COMPLETO", nullable=False)  # COMPLETO, ALERTA_SIMPLES
    destinatarios_notificados = Column(Text, nullable=True)  # JSON com a lista de e-mails/nomes mencionados
    status_envio = Column(String(50), default="PENDENTE", nullable=False, index=True)  # PENDENTE, ENVIADO, FALHA_ENVIO, SIMULADO
    tentativas_envio = Column(Integer, default=0, nullable=False)
    ultimo_erro = Column(Text, nullable=True)
    data_envio = Column(DateTime, nullable=True)
    
    data_criacao = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    data_atualizacao = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("fonte_origem", "id_evento_origem", name="uq_notificacao_evento_origem"),
    )

    def __repr__(self):
        return f"<NotificacaoObito id={self.id} origem={self.fonte_origem} ref={self.id_evento_origem} status={self.status_envio}>"
