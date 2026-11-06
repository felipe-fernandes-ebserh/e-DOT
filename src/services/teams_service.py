"""
Serviço de Envio Assíncrono de Mensagens para o Microsoft Teams
==============================================================
Gerencia a comunicação HTTP com o Webhook de Entrada do Teams, suportando
modo Simulado (Mock) para desenvolvimento e retentativas com backoff exponencial.
"""

import asyncio
import logging
import httpx
from typing import Dict, Any, Optional
from ..config import Settings

logger = logging.getLogger("teams_service")


class TeamsService:
    def __init__(self, webhook_url: Optional[str] = None, max_retries: Optional[int] = None):
        self.webhook_url = webhook_url if webhook_url is not None else Settings.TEAMS_WEBHOOK_URL
        self.max_retries = max_retries if max_retries is not None else Settings.NOTIFICACOES_MAX_RETENTATIVAS
        self.ativo = Settings.TEAMS_NOTIFICACOES_ATIVO

    async def send_notification(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envia o payload de Adaptive Card para o Webhook configurado no Microsoft Teams.
        
        :param payload: Dicionário contendo o cartão formatado.
        :return: Dicionário com resultado da entrega (success, simulated, attempts, error, status_code).
        """
        if not self.ativo:
            logger.info("Envio ao Teams ignorado: TEAMS_NOTIFICACOES_ATIVO=false.")
            return {
                "success": True,
                "simulated": True,
                "status_code": 200,
                "reason": "Notificações desativadas nas configurações",
                "attempts": 0
            }

        # Modo Simulado (Mock): se URL não estiver configurada ou for template de exemplo
        url_limpa = (self.webhook_url or "").strip()
        if not url_limpa or "exemplo" in url_limpa:
            logger.info(f"--- [MODO SIMULADO] Alerta Teams disparado em Mock ---")
            logger.info(f"Payload gerado: {payload}")
            return {
                "success": True,
                "simulated": True,
                "status_code": 200,
                "attempts": 1,
                "error": None
            }

        attempt = 0
        last_error = None
        last_status_code = None

        async with httpx.AsyncClient(timeout=10.0) as client:
            while attempt < self.max_retries:
                attempt += 1
                try:
                    logger.info(f"Enviando alerta ao Teams (tentativa {attempt}/{self.max_retries})...")
                    response = await client.post(url_limpa, json=payload)
                    last_status_code = response.status_code
                    
                    if 200 <= response.status_code < 300:
                        logger.info(f"Alerta entregue com sucesso ao Teams (HTTP {response.status_code}).")
                        return {
                            "success": True,
                            "simulated": False,
                            "status_code": response.status_code,
                            "attempts": attempt,
                            "error": None
                        }
                    else:
                        last_error = f"Erro HTTP {response.status_code}: {response.text}"
                        logger.warning(f"Resposta com erro do Teams na tentativa {attempt}: {last_error}")
                except (httpx.RequestError, httpx.TimeoutException) as exc:
                    last_error = f"Falha de conexão com Teams: {str(exc)}"
                    logger.warning(f"Exceção na tentativa {attempt}: {last_error}")

                # Espera com backoff exponencial antes da próxima tentativa
                if attempt < self.max_retries:
                    backoff = 0.5 * (2 ** (attempt - 1))
                    await asyncio.sleep(backoff)

        logger.error(f"Esgotadas as {self.max_retries} tentativas de envio ao Teams. Último erro: {last_error}")
        return {
            "success": False,
            "simulated": False,
            "status_code": last_status_code,
            "attempts": attempt,
            "error": last_error
        }
