"""
Roteador de Gestão de Usuários e Perfis de Acesso Locais (RBAC)
==============================================================
Endpoints para consulta e atribuição de perfis locais integrados ao Active Directory.
Protegido por padrão (Default-Private Router Pattern).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.auth import auth_handler
from ..resources.database import get_app_db_session
from ..dependencies import verify_coordenacao_or_admin
from ..controllers.usuario_controller import UsuarioController

router = APIRouter(
    prefix="/api/usuarios",
    tags=["Usuarios"],
    dependencies=[Depends(auth_handler.decode_token)]
)


class UsuarioResponseSchema(BaseModel):
    id: int
    username: str
    nome: str
    email: str
    departamento: Optional[str]
    perfil: str
    ativo: bool

    class Config:
        from_attributes = True


class AtribuirPerfilSchema(BaseModel):
    perfil: str = Field(..., description="ADMINISTRADOR, COORDENACAO_CIHDOTT, EQUIPE_BUSCA_ATIVA, CONSULTA")


class AlterarStatusSchema(BaseModel):
    ativo: bool


@router.get("", response_model=List[UsuarioResponseSchema])
async def listar_usuarios(
    db: AsyncSession = Depends(get_app_db_session)
):
    """Lista todos os usuários com acesso configurado na aplicação."""
    return await UsuarioController.listar_usuarios(db)


@router.post(
    "/{username}/perfil",
    response_model=UsuarioResponseSchema,
    dependencies=[Depends(verify_coordenacao_or_admin)]
)
async def atribuir_perfil(
    username: str,
    payload: AtribuirPerfilSchema,
    request: Request,
    current_user: dict = Depends(verify_coordenacao_or_admin),
    db: AsyncSession = Depends(get_app_db_session)
):
    """
    Atribui ou atualiza o perfil de acesso de um usuário.
    Se for um usuário novo, busca os dados cadastrais no Active Directory corporativo.
    Restrito à Coordenação e Administradores.
    """
    operador = current_user.get("username", "sistema")
    ip_origem = getattr(request.client, "host", None) if request.client else None
    return await UsuarioController.atribuir_perfil_usuario(
        db=db,
        username=username,
        perfil=payload.perfil,
        operador=operador,
        ip_origem=ip_origem
    )


@router.put(
    "/{username}/status",
    response_model=UsuarioResponseSchema,
    dependencies=[Depends(verify_coordenacao_or_admin)]
)
async def alterar_status(
    username: str,
    payload: AlterarStatusSchema,
    request: Request,
    current_user: dict = Depends(verify_coordenacao_or_admin),
    db: AsyncSession = Depends(get_app_db_session)
):
    """Ativa ou desativa um usuário do sistema."""
    operador = current_user.get("username", "sistema")
    ip_origem = getattr(request.client, "host", None) if request.client else None
    return await UsuarioController.alternar_status_usuario(
        db=db,
        username=username,
        ativo=payload.ativo,
        operador=operador,
        ip_origem=ip_origem
    )
