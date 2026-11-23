"""
Controller de Notificações de Óbito (CIHDOTT / Microsoft Teams)
==============================================================
Orquestra a busca de destinatários ativos, a prevenção de duplicidades (idempotência),
a formatação do Adaptive Card adaptativo e o despacho assíncrono para o Teams.
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.notificacao_obito import NotificacaoObito
from ..controllers.destinatario_controller import DestinatarioController
from ..helpers.teams_card_helper import build_teams_adaptive_card
from ..services.teams_service import TeamsService
from ..helpers.audit_helper import registrar_auditoria


class NotificacaoObitoController:
    @staticmethod
    async def listar_notificacoes(db: AsyncSession, limit: int = 50) -> List[NotificacaoObito]:
        """Retorna as notificações processadas mais recentes."""
        stmt = select(NotificacaoObito).order_by(NotificacaoObito.id.desc()).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def obter_notificacao(db: AsyncSession, notif_id: int) -> Optional[NotificacaoObito]:
        """Obtém uma notificação pelo seu ID."""
        stmt = select(NotificacaoObito).where(NotificacaoObito.id == notif_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def disparar_notificacao_obito(
        db: AsyncSession,
        dados_obito: Dict[str, Any],
        operador: str,
        fonte_origem: str = "CONTINGENCIA",
        destinatarios: Optional[List[Dict[str, str]]] = None,
        apenas_simular: bool = False,
        ip_origem: Optional[str] = None
    ) -> NotificacaoObito:
        """
        Executa o pipeline de notificação de óbito:
        1. Validação de idempotência por chave de evento.
        2. Coleta de destinatários ativos (ou usa lista customizada).
        3. Montagem de cartão adaptativo com @menções nominais.
        4. Despacho assíncrono para o Microsoft Teams (ou simulação controlada).
        5. Persistência de status e auditoria clínica.
        """
        id_evento = str(dados_obito.get("id_evento_origem", "")).strip()
        if not id_evento:
            id_evento = f"EVT-{int(datetime.now(timezone.utc).timestamp())}"

        # 1. Checagem de Idempotência
        stmt = select(NotificacaoObito).where(
            NotificacaoObito.fonte_origem == fonte_origem,
            NotificacaoObito.id_evento_origem == id_evento
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            # Já processado anteriormente: retorna registro existente sem reenviar duplicado
            return existing

        # 2. Coleta de destinatários
        if destinatarios is not None:
            lista_destinatarios = destinatarios
        else:
            destinatarios_db = await DestinatarioController.listar_destinatarios(db, apenas_ativos=True)
            lista_destinatarios = [
                {"nome": d.nome, "email_teams": d.email_teams}
                for d in destinatarios_db
            ]

        # 3. Identifica Modo de Apresentação
        nome_paciente = dados_obito.get("nome_paciente")
        modo = "COMPLETO" if (nome_paciente and str(nome_paciente).strip()) else "ALERTA_SIMPLES"

        # 4. Constrói Adaptive Card
        card_payload = build_teams_adaptive_card(dados_obito, lista_destinatarios)

        # Normaliza data_hora_obito para objeto datetime
        data_obito_val = dados_obito.get("data_hora_obito")
        if isinstance(data_obito_val, str):
            try:
                data_obito = datetime.fromisoformat(data_obito_val)
                if data_obito.tzinfo is None:
                    data_obito = data_obito.replace(tzinfo=timezone.utc)
            except Exception:
                data_obito = datetime.now(timezone.utc)
        elif isinstance(data_obito_val, datetime):
            data_obito = data_obito_val
        else:
            data_obito = datetime.now(timezone.utc)

        # 5. Cria registro inicial
        notif = NotificacaoObito(
            fonte_origem=fonte_origem,
            id_evento_origem=id_evento,
            nome_paciente=nome_paciente,
            idade=dados_obito.get("idade"),
            sexo=dados_obito.get("sexo"),
            causa_morte=dados_obito.get("causa_morte"),
            setor_leito=dados_obito.get("setor_leito"),
            prontuario=dados_obito.get("prontuario"),
            data_hora_obito=data_obito,
            modo_apresentacao=modo,
            destinatarios_notificados=json.dumps(lista_destinatarios, ensure_ascii=False),
            status_envio="PENDENTE",
            tentativas_envio=0
        )
        db.add(notif)
        await db.commit()
        await db.refresh(notif)

        # 6. Despacho para o Teams (ou Simulação sem disparo externo)
        if apenas_simular:
            envio_res = {
                "success": True,
                "simulated": True,
                "status_code": 200,
                "attempts": 1,
                "error": None
            }
        else:
            teams_service = TeamsService()
            envio_res = await teams_service.send_notification(card_payload)

        notif.tentativas_envio = envio_res.get("attempts", 1)
        if envio_res.get("success"):
            notif.status_envio = "SIMULADO" if envio_res.get("simulated") else "ENVIADO"
            notif.data_envio = datetime.now(timezone.utc)
            notif.ultimo_erro = None
        else:
            notif.status_envio = "FALHA_ENVIO"
            notif.ultimo_erro = envio_res.get("error")

        await db.commit()
        await db.refresh(notif)

        # 7. Trilha de Auditoria
        await registrar_auditoria(
            db=db,
            usuario=operador,
            categoria="NEGOCIO_CLINICO",
            acao="DISPARAR_NOTIFICACAO_OBITO",
            recurso=f"notificacao:{notif.id}",
            dados_anteriores=None,
            dados_novos={
                "id": notif.id,
                "fonte": notif.fonte_origem,
                "modo": notif.modo_apresentacao,
                "status": notif.status_envio,
                "destinatarios_total": len(lista_destinatarios),
                "simulado": apenas_simular or envio_res.get("simulated", False)
            },
            ip_origem=ip_origem
        )

        return notif

    @staticmethod
    async def disparar_teste_teams(
        db: AsyncSession,
        operador: str,
        modo: str = "COMPLETO",
        dados_obito: Optional[Dict[str, Any]] = None,
        apenas_simular: bool = False,
        destinatarios_ids: Optional[List[int]] = None,
        notificar_apenas_operador: bool = False,
        current_user: Optional[Dict[str, Any]] = None,
        ip_origem: Optional[str] = None
    ) -> NotificacaoObito:
        """
        Dispara um alerta de teste para o canal do Microsoft Teams permitindo validar
        a entrega de alertas nos smartphones da equipe.
        Permite customização de dados do óbito/alerta, controle de simulação e seleção de destinatários.
        """
        uid = uuid.uuid4().hex[:6]
        ts = int(datetime.now(timezone.utc).timestamp())
        modo_upper = modo.strip().upper()

        if modo_upper == "ALERTA_SIMPLES":
            dados_teste = {
                "id_evento_origem": f"TESTE-SIMPLES-{ts}-{uid}",
                "nome_paciente": None,
                "setor_leito": "UTI Geral - Leito 04 (Simulação)",
                "causa_morte": None,
                "prontuario": None,
                "data_hora_obito": datetime.now(timezone.utc)
            }
        else:
            dados_teste = {
                "id_evento_origem": f"TESTE-COMPLETO-{ts}-{uid}",
                "nome_paciente": "Paciente Simulado de Teste (CIHDOTT)",
                "idade": 52,
                "setor_leito": "UTI Coronariana - Leito 02 (Simulação)",
                "causa_morte": "Choque Cardiogênico (Teste de Notificação)",
                "prontuario": "TESTE-12345",
                "data_hora_obito": datetime.now(timezone.utc)
            }

        # Mescla dados customizados se fornecidos
        if dados_obito and isinstance(dados_obito, dict):
            for k, v in dados_obito.items():
                if v is not None and v != "":
                    dados_teste[k] = v

        # Definição dos destinatários para o teste
        lista_destinatarios: Optional[List[Dict[str, str]]] = None

        if notificar_apenas_operador:
            current_user = current_user or {}
            nome = current_user.get("nome") or current_user.get("displayName") or operador
            email = current_user.get("email") or f"{operador}@ebserh.gov.br"
            if isinstance(nome, list) and nome:
                nome = nome[0]
            if isinstance(email, list) and email:
                email = email[0]
            lista_destinatarios = [{"nome": str(nome), "email_teams": str(email)}]
        elif destinatarios_ids is not None:
            if len(destinatarios_ids) == 0:
                lista_destinatarios = []
            else:
                destinatarios_db = await DestinatarioController.listar_destinatarios(db, apenas_ativos=True)
                lista_destinatarios = [
                    {"nome": d.nome, "email_teams": d.email_teams}
                    for d in destinatarios_db
                    if d.id in destinatarios_ids
                ]

        return await NotificacaoObitoController.disparar_notificacao_obito(
            db=db,
            dados_obito=dados_teste,
            operador=operador,
            fonte_origem="TESTE",
            destinatarios=lista_destinatarios,
            apenas_simular=apenas_simular,
            ip_origem=ip_origem
        )

    @staticmethod
    async def sincronizar_obitos_csh(
        db: AsyncSession,
        operador: str = "SISTEMA_POLLING",
        limite: int = 50,
        apenas_simular: bool = False
    ) -> Dict[str, Any]:
        """Varre o banco CSH em busca de solicitações de declaração de óbito pendentes,
        aplica idempotência estrita e dispara alertas no Microsoft Teams.
        """
        from ..providers.implementations.obito_mysql_provider import ObitoMySqlProvider

        provider = ObitoMySqlProvider()
        chamados = await provider.buscar_obitos_pendentes(limite=limite)

        total_encontrados = len(chamados)
        novos_notificados = 0
        ignorados_duplicados = 0
        falhas = 0
        detalhes = []

        for item in chamados:
            id_evento = str(item.get("id_evento_origem") or item.get("id_chamado_material"))
            
            # Checagem de idempotência antes de disparar
            stmt = select(NotificacaoObito).where(
                NotificacaoObito.fonte_origem == "CSH_MYSQL",
                NotificacaoObito.id_evento_origem == id_evento
            )
            existente = (await db.execute(stmt)).scalar_one_or_none()

            if existente:
                ignorados_duplicados += 1
                detalhes.append({
                    "id_chamado": id_evento,
                    "status": "IGNORADO_DUPLICADO",
                    "notificacao_id": existente.id
                })
                continue

            # Mapeia campos do chamado CSH para dados de óbito esperados
            solicitante = item.get("medico_responsavel") or item.get("solicitante") or "Não informado"
            ramal = item.get("ramal_contato") or item.get("ramal") or ""
            obs = item.get("causa_obito") or item.get("obs") or ""
            setor_origem = item.get("setor_solicitante") or item.get("setor_obito") or "Setor não informado"
            
            detalhe_extra = f"Solicitante: {solicitante}"
            if ramal:
                detalhe_extra += f" (Ramal: {ramal})"
            if obs:
                detalhe_extra += f" | Obs: {obs}"

            dados_obito = {
                "id_evento_origem": id_evento,
                "descricao_ocorrencia": f"Solicitação de Declaração de Óbito no CSH (#{id_evento})",
                "nome_paciente": None,  # Não exibe campo de paciente pois na solicitação de material não há paciente cadastrado
                "setor_leito": f"{setor_origem}",
                "causa_morte": detalhe_extra,
                "prontuario": None,
                "data_hora_obito": item.get("data_hora_obito") or datetime.now(timezone.utc)
            }

            try:
                notif = await NotificacaoObitoController.disparar_notificacao_obito(
                    db=db,
                    dados_obito=dados_obito,
                    operador=operador,
                    fonte_origem="CSH_MYSQL",
                    apenas_simular=apenas_simular
                )
                novos_notificados += 1
                detalhes.append({
                    "id_chamado": id_evento,
                    "status": notif.status_envio,
                    "notificacao_id": notif.id
                })
            except Exception as e:
                falhas += 1
                detalhes.append({
                    "id_chamado": id_evento,
                    "status": "ERRO",
                    "erro": str(e)
                })

        return {
            "total_encontrados": total_encontrados,
            "novos_notificados": novos_notificados,
            "ignorados_duplicados": ignorados_duplicados,
            "falhas": falhas,
            "detalhes": detalhes
        }
