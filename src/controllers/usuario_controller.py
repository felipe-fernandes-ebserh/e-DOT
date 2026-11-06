"""
Controller de Gestão de Usuários e Perfis de Acesso Locais (RBAC)
================================================================
Centraliza as operações de consulta, criação, atribuição de perfis e auditoria
de usuários da aplicação integrados ao Active Directory corporativo.
"""

from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.usuario import UsuarioSistema
from ..auth.auth import auth_handler
from ..helpers.audit_helper import registrar_auditoria

PERFIS_PERMITIDOS = [
    "ADMINISTRADOR",
    "COORDENACAO_CIHDOTT",
    "EQUIPE_BUSCA_ATIVA",
    "CONSULTA"
]


class UsuarioController:
    @staticmethod
    async def listar_usuarios(db: AsyncSession) -> List[UsuarioSistema]:
        """Retorna todos os usuários cadastrados na base local."""
        stmt = select(UsuarioSistema).order_by(UsuarioSistema.nome)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def obter_usuario_por_username(db: AsyncSession, username: str) -> Optional[UsuarioSistema]:
        """Obtém um usuário pelo login do AD."""
        stmt = select(UsuarioSistema).where(UsuarioSistema.username == username.strip().lower())
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def atribuir_perfil_usuario(
        db: AsyncSession,
        username: str,
        perfil: str,
        operador: str,
        ip_origem: Optional[str] = None
    ) -> UsuarioSistema:
        """
        Atribui ou atualiza o perfil de acesso de um usuário. Se o usuário ainda não
        estiver na tabela local, consulta o AD corporativo para preencher seus dados.
        """
        clean_username = username.strip().lower()
        clean_perfil = perfil.strip().upper()

        if clean_perfil not in PERFIS_PERMITIDOS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Perfil inválido: '{perfil}'. Opções permitidas: {', '.join(PERFIS_PERMITIDOS)}"
            )

        user_db = await UsuarioController.obter_usuario_por_username(db, clean_username)

        if user_db:
            dados_anteriores = {
                "perfil": user_db.perfil,
                "ativo": user_db.ativo
            }
            user_db.perfil = clean_perfil
            await db.commit()
            await db.refresh(user_db)

            dados_novos = {
                "perfil": user_db.perfil,
                "ativo": user_db.ativo
            }

            await registrar_auditoria(
                db=db,
                usuario=operador,
                categoria="SEGURANCA",
                acao="ALTERAR_PERFIL_USUARIO",
                recurso=f"usuario:{clean_username}",
                dados_anteriores=dados_anteriores,
                dados_novos=dados_novos,
                ip_origem=ip_origem
            )
            return user_db

        # Usuário novo: Pré-validação no Active Directory
        ad_info = auth_handler.search_ad_user(clean_username)
        if not ad_info.get("exists", False):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário '{clean_username}' não foi localizado no Active Directory corporativo."
            )

        novo_usuario = UsuarioSistema(
            username=clean_username,
            nome=ad_info.get("displayName") or clean_username,
            email=ad_info.get("email") or f"{clean_username}@ebserh.gov.br",
            departamento=ad_info.get("department") or "HC-UFPE / EBSERH",
            perfil=clean_perfil,
            ativo=True
        )
        db.add(novo_usuario)
        await db.commit()
        await db.refresh(novo_usuario)

        await registrar_auditoria(
            db=db,
            usuario=operador,
            categoria="SEGURANCA",
            acao="CRIAR_USUARIO_LOCAL",
            recurso=f"usuario:{clean_username}",
            dados_anteriores=None,
            dados_novos={"username": clean_username, "perfil": clean_perfil, "nome": novo_usuario.nome},
            ip_origem=ip_origem
        )

        return novo_usuario

    @staticmethod
    async def alternar_status_usuario(
        db: AsyncSession,
        username: str,
        ativo: bool,
        operador: str,
        ip_origem: Optional[str] = None
    ) -> UsuarioSistema:
        """Ativa ou inativa o acesso de um usuário ao sistema."""
        clean_username = username.strip().lower()
        user_db = await UsuarioController.obter_usuario_por_username(db, clean_username)
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário '{clean_username}' não encontrado na base local."
            )

        dados_ant = {"ativo": user_db.ativo}
        user_db.ativo = ativo
        await db.commit()
        await db.refresh(user_db)

        await registrar_auditoria(
            db=db,
            usuario=operador,
            categoria="SEGURANCA",
            acao="ALTERAR_STATUS_USUARIO",
            recurso=f"usuario:{clean_username}",
            dados_anteriores=dados_ant,
            dados_novos={"ativo": user_db.ativo},
            ip_origem=ip_origem
        )
        return user_db
