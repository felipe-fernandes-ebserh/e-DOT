"""
Roteador de Notificações de Óbito e Gestão de Destinatários do Teams
===================================================================
Endpoints protegidos por padrão (Default-Private Router Pattern) para envio
de alertas ao Microsoft Teams, simulação de testes e gerenciamento da equipe.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Request, status, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.auth import auth_handler
from ..resources.database import get_app_db_session
from ..dependencies import verify_coordenacao_or_admin
from ..controllers.destinatario_controller import DestinatarioController
from ..controllers.notificacao_obito_controller import NotificacaoObitoController

router = APIRouter(
    prefix="/api/notificacoes",
    tags=["Notificacoes"],
    dependencies=[Depends(auth_handler.decode_token)]
)


# --- Schemas Pydantic ---
class DestinatarioCreateSchema(BaseModel):
    nome: str = Field(..., description="Nome do profissional da busca ativa")
    email_teams: str = Field(..., description="E-mail institucional do Microsoft Teams (UPN)")
    cargo_setor: Optional[str] = Field(None, description="Cargo ou setor hospitalar")


class DestinatarioUpdateSchema(BaseModel):
    nome: Optional[str] = None
    email_teams: Optional[str] = None
    cargo_setor: Optional[str] = None
    ativo: Optional[bool] = None


class DestinatarioResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email_teams: str
    cargo_setor: Optional[str]
    ativo: bool


class TesteTeamsSchema(BaseModel):
    modo: str = Field(default="COMPLETO", description="Modo do teste: 'COMPLETO' ou 'ALERTA_SIMPLES'")
    dados_obito: Optional[Dict[str, Any]] = Field(default=None, description="Dados clínicos/operacionais customizados para o teste")
    apenas_simular: bool = Field(default=False, description="Se True, não despacha para o Teams e grava como SIMULADO")
    destinatarios_ids: Optional[List[int]] = Field(default=None, description="IDs dos destinatários a mencionar. Lista vazia [] = sem menções")
    notificar_apenas_operador: bool = Field(default=False, description="Se True, menciona apenas o usuário logado que disparou o teste")


class NotificacaoObitoCreateSchema(BaseModel):
    fonte_origem: Optional[str] = Field(default="CONTINGENCIA")
    id_evento_origem: Optional[str] = None
    nome_paciente: Optional[str] = None
    idade: Optional[int] = None
    sexo: Optional[str] = None
    causa_morte: Optional[str] = None
    setor_leito: Optional[str] = None
    prontuario: Optional[str] = None


class NotificacaoResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fonte_origem: str
    id_evento_origem: str
    nome_paciente: Optional[str] = None
    prontuario: Optional[str] = None
    setor_leito: Optional[str] = None
    modo_apresentacao: str
    status_envio: str
    tentativas_envio: int
    ultimo_erro: Optional[str] = None


# --- Endpoints de Destinatários ---
@router.get("/destinatarios", response_model=List[DestinatarioResponseSchema])
async def listar_destinatarios(
    apenas_ativos: bool = False,
    db: AsyncSession = Depends(get_app_db_session)
):
    """Lista os destinatários cadastrados para receber notificações no Teams."""
    return await DestinatarioController.listar_destinatarios(db, apenas_ativos=apenas_ativos)


@router.post(
    "/destinatarios",
    response_model=DestinatarioResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_coordenacao_or_admin)]
)
async def criar_destinatario(
    payload: DestinatarioCreateSchema,
    request: Request,
    current_user: dict = Depends(verify_coordenacao_or_admin),
    db: AsyncSession = Depends(get_app_db_session)
):
    """Cadastra um novo membro na equipe de busca ativa. Restrito a Administradores e Coordenação."""
    operador = current_user.get("username", "sistema")
    ip_origem = getattr(request.client, "host", None) if request.client else None
    return await DestinatarioController.criar_destinatario(
        db=db,
        nome=payload.nome,
        email_teams=payload.email_teams,
        cargo_setor=payload.cargo_setor,
        operador=operador,
        ip_origem=ip_origem
    )


@router.put(
    "/destinatarios/{destinatario_id}",
    response_model=DestinatarioResponseSchema,
    dependencies=[Depends(verify_coordenacao_or_admin)]
)
async def atualizar_destinatario(
    destinatario_id: int,
    payload: DestinatarioUpdateSchema,
    request: Request,
    current_user: dict = Depends(verify_coordenacao_or_admin),
    db: AsyncSession = Depends(get_app_db_session)
):
    """Atualiza dados cadastrais ou ativa/inativa um membro da equipe."""
    operador = current_user.get("username", "sistema")
    ip_origem = getattr(request.client, "host", None) if request.client else None
    return await DestinatarioController.atualizar_destinatario(
        db=db,
        destinatario_id=destinatario_id,
        nome=payload.nome,
        email_teams=payload.email_teams,
        cargo_setor=payload.cargo_setor,
        ativo=payload.ativo,
        operador=operador,
        ip_origem=ip_origem
    )


@router.delete(
    "/destinatarios/{destinatario_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_coordenacao_or_admin)]
)
async def remover_destinatario(
    destinatario_id: int,
    request: Request,
    current_user: dict = Depends(verify_coordenacao_or_admin),
    db: AsyncSession = Depends(get_app_db_session)
):
    """Exclui um profissional da lista de destinatários do Teams."""
    operador = current_user.get("username", "sistema")
    ip_origem = getattr(request.client, "host", None) if request.client else None
    await DestinatarioController.remover_destinatario(
        db=db,
        destinatario_id=destinatario_id,
        operador=operador,
        ip_origem=ip_origem
    )
    return {"detail": "Destinatário removido com sucesso"}


# --- Endpoints de Disparo e Teste ---
@router.post(
    "/teste-teams",
    response_model=NotificacaoResponseSchema,
    dependencies=[Depends(verify_coordenacao_or_admin)]
)
async def disparar_teste_teams(
    payload: TesteTeamsSchema,
    request: Request,
    current_user: dict = Depends(verify_coordenacao_or_admin),
    db: AsyncSession = Depends(get_app_db_session)
):
    """
    Dispara um alerta de teste para o canal do Microsoft Teams (Modo Completo ou Modo Alerta Simples).
    Permite validar a entrega de alertas sonoros e push no celular dos membros da equipe.
    """
    operador = current_user.get("username", "sistema")
    ip_origem = getattr(request.client, "host", None) if request.client else None
    return await NotificacaoObitoController.disparar_teste_teams(
        db=db,
        operador=operador,
        modo=payload.modo,
        dados_obito=payload.dados_obito,
        apenas_simular=payload.apenas_simular,
        destinatarios_ids=payload.destinatarios_ids,
        notificar_apenas_operador=payload.notificar_apenas_operador,
        current_user=current_user,
        ip_origem=ip_origem
    )


@router.post("/obitos", response_model=NotificacaoResponseSchema)
async def registrar_e_disparar_obito(
    payload: NotificacaoObitoCreateSchema,
    request: Request,
    current_user: dict = Depends(auth_handler.decode_token),
    db: AsyncSession = Depends(get_app_db_session)
):
    """
    Registra um óbito (contingência ou integração) e despacha a notificação correspondente ao Teams.
    """
    operador = current_user.get("username", "sistema")
    ip_origem = getattr(request.client, "host", None) if request.client else None
    return await NotificacaoObitoController.disparar_notificacao_obito(
        db=db,
        dados_obito=payload.model_dump(),
        operador=operador,
        fonte_origem=payload.fonte_origem or "CONTINGENCIA",
        ip_origem=ip_origem
    )


@router.get(
    "/csh/teste-conexao",
    dependencies=[Depends(verify_coordenacao_or_admin)]
)
async def testar_conexao_csh():
    """Testa a conectividade com o banco MySQL do CSH e lista prévia de solicitações."""
    from ..providers.implementations.obito_mysql_provider import ObitoMySqlProvider
    provider = ObitoMySqlProvider()
    diagnostico = await provider.testar_conexao()
    amostra = []
    if diagnostico.get("status") == "sucesso":
        try:
            amostra = await provider.buscar_obitos_pendentes(limite=5)
        except Exception as e:
            diagnostico["erro_busca"] = str(e)
    return {
        "diagnostico": diagnostico,
        "total_amostra": len(amostra),
        "amostra": amostra
    }


@router.post(
    "/csh/sincronizar",
    dependencies=[Depends(verify_coordenacao_or_admin)]
)
async def sincronizar_csh_manual(
    limite: int = 50,
    apenas_simular: bool = False,
    current_user: dict = Depends(verify_coordenacao_or_admin),
    db: AsyncSession = Depends(get_app_db_session)
):
    """Executa a sincronização manual de chamados de DO do CSH."""
    operador = current_user.get("username", "admin")
    return await NotificacaoObitoController.sincronizar_obitos_csh(
        db=db,
        operador=operador,
        limite=limite,
        apenas_simular=apenas_simular
    )


@router.get("/obitos", response_model=List[NotificacaoResponseSchema])
async def listar_historico_notificacoes(
    limit: int = 50,
    db: AsyncSession = Depends(get_app_db_session)
):
    """Lista o histórico de notificações e status de entrega ao Teams."""
    return await NotificacaoObitoController.listar_notificacoes(db=db, limit=limit)
