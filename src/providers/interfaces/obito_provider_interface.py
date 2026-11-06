from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class ObitoProviderInterface(ABC):
    """Interface (contrato) para provedores de dados de óbitos hospitalares."""

    @abstractmethod
    async def buscar_obitos_pendentes(self, limite: int = 50) -> List[Dict[str, Any]]:
        """Busca óbitos registrados recentemente que ainda não foram notificados.
        
        Deve retornar uma lista de dicionários contendo ao menos:
        - id_evento_origem (identificador único no sistema de origem)
        - fonte_origem (ex: 'CSH_MYSQL')
        - setor_obito / unidade
        - leito
        - data_hora_obito
        - paciente_nome (opcional para Modo Alerta Simples)
        - prontuario (opcional)
        """
        pass

    @abstractmethod
    async def marcar_obito_notificado(self, id_evento_origem: str) -> bool:
        """Marca opcionalmente no sistema de origem que o óbito foi processado."""
        pass
