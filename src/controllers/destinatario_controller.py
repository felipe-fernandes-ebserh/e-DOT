"""
Controller de Gestão de Destinatários da Notificação do Microsoft Teams
=======================================================================
Permite à coordenação da CIHDOTT e administradores listar, cadastrar,
atualizar e remover os integrantes que recebem os alertas móveis no canal do Teams.
"""

from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.destinatario_notificacao import DestinatarioNotificacao
from ..helpers.audit_helper import registrar_auditoria


class DestinatarioController:
    @staticmethod
    async def listar_destinatarios(db: AsyncSession, apenas_ativos: bool = False) -> List[DestinatarioNotificacao]:
        """Retorna os destinatários cadastrados, com opção de filtrar apenas os ativos."""
        stmt = select(DestinatarioNotificacao)
        if apenas_ativos:
            stmt = stmt.where(DestinatarioNotificacao.ativo == True)
        stmt = stmt.order_by(DestinatarioNotificacao.nome)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def obter_destinatario_por_id(db: AsyncSession, destinatario_id: int) -> Optional[DestinatarioNotificacao]:
        """Busca um destinatário pela chave primária."""
        stmt = select(DestinatarioNotificacao).where(DestinatarioNotificacao.id == destinatario_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def criar_destinatario(
        db: AsyncSession,
        nome: str,
        email_teams: str,
        cargo_setor: Optional[str],
        operador: str,
        ip_origem: Optional[str] = None
    ) -> DestinatarioNotificacao:
        """Cadastra um novo profissional para receber os alertas no Teams."""
        clean_nome = nome.strip()
        clean_email = email_teams.strip().lower()

        if not clean_nome or not clean_email or "@" not in clean_email or "." not in clean_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome e e-mail institucional corporativo válido são obrigatórios."
            )

        # Checa duplicidade de e-mail
        stmt = select(DestinatarioNotificacao).where(DestinatarioNotificacao.email_teams == clean_email)
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe um destinatário cadastrado com o e-mail '{clean_email}'."
            )

        dest = DestinatarioNotificacao(
            nome=clean_nome,
            email_teams=clean_email,
            cargo_setor=cargo_setor.strip() if cargo_setor else None,
            ativo=True
        )
        db.add(dest)
        await db.commit()
        await db.refresh(dest)

        await registrar_auditoria(
            db=db,
            usuario=operador,
            categoria="CONFIGURACAO",
            acao="CRIAR_DESTINATARIO_NOTIFICACAO",
            recurso=f"destinatario:{dest.id}",
            dados_anteriores=None,
            dados_novos={"id": dest.id, "nome": dest.nome, "email_teams": dest.email_teams, "ativo": dest.ativo},
            ip_origem=ip_origem
        )

        return dest

    @staticmethod
    async def atualizar_destinatario(
        db: AsyncSession,
        destinatario_id: int,
        nome: Optional[str] = None,
        email_teams: Optional[str] = None,
        cargo_setor: Optional[str] = None,
        ativo: Optional[bool] = None,
        operador: str = "sistema",
        ip_origem: Optional[str] = None
    ) -> DestinatarioNotificacao:
        """Atualiza dados cadastrais ou status de um destinatário."""
        dest = await DestinatarioController.obter_destinatario_por_id(db, destinatario_id)
        if not dest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destinatário ID {destinatario_id} não encontrado."
            )

        dados_ant = {
            "nome": dest.nome,
            "email_teams": dest.email_teams,
            "cargo_setor": dest.cargo_setor,
            "ativo": dest.ativo
        }

        if nome is not None and nome.strip():
            dest.nome = nome.strip()
        if email_teams is not None and email_teams.strip():
            clean_email = email_teams.strip().lower()
            if "@" not in clean_email or "." not in clean_email:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail inválido.")
            # Checa se outro registro já tem esse e-mail
            stmt = select(DestinatarioNotificacao).where(
                DestinatarioNotificacao.email_teams == clean_email,
                DestinatarioNotificacao.id != destinatario_id
            )
            conflict = (await db.execute(stmt)).scalar_one_or_none()
            if conflict:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já utilizado por outro destinatário.")
            dest.email_teams = clean_email
        if cargo_setor is not None:
            dest.cargo_setor = cargo_setor.strip() if cargo_setor else None
        if ativo is not None:
            dest.ativo = ativo

        await db.commit()
        await db.refresh(dest)

        dados_novos = {
            "nome": dest.nome,
            "email_teams": dest.email_teams,
            "cargo_setor": dest.cargo_setor,
            "ativo": dest.ativo
        }

        await registrar_auditoria(
            db=db,
            usuario=operador,
            categoria="CONFIGURACAO",
            acao="ATUALIZAR_DESTINATARIO_NOTIFICACAO",
            recurso=f"destinatario:{dest.id}",
            dados_anteriores=dados_ant,
            dados_novos=dados_novos,
            ip_origem=ip_origem
        )

        return dest

    @staticmethod
    async def remover_destinatario(
        db: AsyncSession,
        destinatario_id: int,
        operador: str,
        ip_origem: Optional[str] = None
    ) -> bool:
        """Remove um destinatário do banco de dados."""
        dest = await DestinatarioController.obter_destinatario_por_id(db, destinatario_id)
        if not dest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destinatário ID {destinatario_id} não encontrado."
            )

        dados_ant = {
            "id": dest.id,
            "nome": dest.nome,
            "email_teams": dest.email_teams
        }

        await db.delete(dest)
        await db.commit()

        await registrar_auditoria(
            db=db,
            usuario=operador,
            categoria="CONFIGURACAO",
            acao="EXCLUIR_DESTINATARIO_NOTIFICACAO",
            recurso=f"destinatario:{destinatario_id}",
            dados_anteriores=dados_ant,
            dados_novos=None,
            ip_origem=ip_origem
        )

        return True
