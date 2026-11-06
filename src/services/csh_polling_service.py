"""
Serviço de Background Polling para Ingestão Contínua do CSH
============================================================
Monitora periodicamente o banco MySQL do CSH em busca de novas solicitações
de Declaração de Óbito e aciona as notificações do Microsoft Teams de forma
assíncrona e resiliente.
"""

import asyncio
import logging
from typing import Optional

from ..config import (
    CSH_POLLING_ATIVO,
    CSH_POLLING_INTERVALO_SEGUNDOS,
    CSH_MYSQL_URL
)
from ..resources.database import DatabaseManager
from ..controllers.notificacao_obito_controller import NotificacaoObitoController

logger = logging.getLogger("csh_polling")


class CshPollingService:
    def __init__(
        self,
        app_db: DatabaseManager,
        intervalo_segundos: Optional[int] = None,
        ativo: Optional[bool] = None
    ):
        self.app_db = app_db
        self.intervalo = intervalo_segundos or CSH_POLLING_INTERVALO_SEGUNDOS
        self.ativo = ativo if ativo is not None else CSH_POLLING_ATIVO
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def _loop(self):
        logger.info(f"Iniciando serviço de background polling CSH (intervalo: {self.intervalo}s)...")
        while self._running:
            try:
                # Obtém sessão assíncrona do banco local através do sessionmaker do app_db
                async with self.app_db.async_session_maker() as db:
                    resultado = await NotificacaoObitoController.sincronizar_obitos_csh(
                        db=db,
                        operador="SISTEMA_POLLING",
                        limite=50
                    )
                    if resultado.get("novos_notificados", 0) > 0:
                        logger.info(
                            f"[CSH Polling] {resultado['novos_notificados']} novo(s) óbito(s) notificado(s) com sucesso. "
                            f"(Ignorados/Duplicados: {resultado['ignorados_duplicados']})"
                        )
                    else:
                        logger.debug(f"[CSH Polling] Varredura concluída. Nenhum novo óbito. Ignorados/Já existentes: {resultado.get('ignorados_duplicados', 0)}")
            except Exception as e:
                logger.error(f"[CSH Polling] Erro durante ciclo de sincronização: {e}", exc_info=True)

            try:
                await asyncio.sleep(self.intervalo)
            except asyncio.CancelledError:
                break

        logger.info("Serviço de background polling CSH finalizado.")

    def start(self):
        if not self.ativo:
            logger.info("Background polling CSH está desativado (CSH_POLLING_ATIVO=false).")
            return

        if not CSH_MYSQL_URL or "usuario_csh" in CSH_MYSQL_URL:
            logger.info("CSH_MYSQL_URL não configurada para polling contínuo. Serviço em pausa.")
            return

        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._loop())

    async def stop(self):
        if self._running:
            self._running = False
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass

