import os
from typing import Callable
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .providers.interfaces.paciente_provider_interface import PacienteProviderInterface
from .providers.implementations.paciente_postgres_provider import PacientePostgresProvider
from .providers.implementations.paciente_csv_provider import PacienteCsvProvider
from .resources.database import get_aghu_db_session

# 1. Funções "getter" simples e independentes (privadas por convenção)
def _get_paciente_postgres_provider(
    session: AsyncSession = Depends(get_aghu_db_session)
) -> PacienteProviderInterface:
    return PacientePostgresProvider(session=session)

def _get_paciente_csv_provider() -> PacienteProviderInterface:
    csv_path = os.getenv("PACIENTE_CSV_PATH", "data/pacientes.csv")
    return PacienteCsvProvider(csv_path=csv_path)

# 2. A FÁBRICA: A única função que o roteador vai conhecer.
def get_paciente_provider(strategy: str) -> Callable[..., PacienteProviderInterface]:
    """
    Esta é uma fábrica. Baseado na string 'strategy', ela não retorna o provedor,
    mas sim a FUNÇÃO DE DEPENDÊNCIA correta que o FastAPI deve usar.
    """
    if strategy.upper() == "POSTGRES":
        return _get_paciente_postgres_provider
    elif strategy.upper() == "CSV":
        return _get_paciente_csv_provider
    else:
        raise ValueError(f"Estratégia de provedor desconhecida: {strategy}")


# 3. CONTROLE DE ACESSO RBAC LOCAL (CIHDOTT & ADMINISTRAÇÃO)
from fastapi import HTTPException, status
from sqlalchemy import select
from .auth.auth import auth_handler
from .resources.database import get_app_db_session
from .models.usuario import UsuarioSistema

async def verify_coordenacao_or_admin(
    current_user: dict = Depends(auth_handler.decode_token),
    db: AsyncSession = Depends(get_app_db_session)
) -> dict:
    """
    Valida se o usuário autenticado possui perfil de COORDENACAO_CIHDOTT ou ADMINISTRADOR
    na tabela local, ou se pertence ao grupo de administradores da TI no AD (GLO-SEC-HCPE-SETISD).
    Lança HTTP 403 Forbidden caso não possua privilégios suficientes.
    """
    groups = current_user.get("groups", [])
    ADMIN_GROUP = "GLO-SEC-HCPE-SETISD"
    if ADMIN_GROUP in groups:
        return current_user

    username = current_user.get("username") or current_user.get("sub")
    if username == "admin":
        return current_user

    stmt = select(UsuarioSistema).where(UsuarioSistema.username == username, UsuarioSistema.ativo == True)
    result = await db.execute(stmt)
    user_db = result.scalar_one_or_none()

    if not user_db or user_db.perfil not in ("ADMINISTRADOR", "COORDENACAO_CIHDOTT"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: recurso restrito à Coordenação da CIHDOTT e Administradores."
        )

    return {
        **current_user,
        "perfil": user_db.perfil,
        "nome": user_db.nome,
        "usuario_id": user_db.id
    }

