import os
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from ...config import (
    CSH_MYSQL_URL,
    CSH_ID_TIPO_MATERIAL_OBITO,
    CSH_ID_LOCAL_TRIAGEM_OBSTETRICA,
    normalizar_mysql_url
)
from ...helpers.sql_helper import read_sql_file, create_query
from ..interfaces.obito_provider_interface import ObitoProviderInterface

logger = logging.getLogger(__name__)

class ObitoMySqlProvider(ObitoProviderInterface):
    """Provedor de dados para leitura de eventos de solicitação de óbito do banco MySQL do CSH.
    
    Suporta injeção de uma sessão existente ou conexão sob demanda usando CSH_MYSQL_URL normalizada.
    Possui modo de contingência/mock caso o banco do CSH não esteja configurado ou acessível.
    """

    def __init__(
        self,
        session: Optional[AsyncSession] = None,
        database_url: Optional[str] = None,
        id_tipo_material: Optional[int] = None,
        id_local_destino: Optional[int] = None
    ):
        self.session = session
        raw_url = database_url or CSH_MYSQL_URL
        self.database_url = normalizar_mysql_url(raw_url, async_driver=True) if raw_url else ""
        self.id_tipo_material = id_tipo_material or CSH_ID_TIPO_MATERIAL_OBITO
        self.id_local_destino = id_local_destino or CSH_ID_LOCAL_TRIAGEM_OBSTETRICA
        self._engine = None

    def _get_sql_query(self, filename: str, params: Optional[dict] = None) -> str:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sql_file_path = os.path.join(base_dir, '..', 'sql', 'csh', filename)
        sql_content = read_sql_file(sql_file_path)
        if params:
            sql_content = create_query(sql_content, params)
        return sql_content

    async def buscar_obitos_pendentes(
        self,
        limite: int = 50,
        id_tipo_material: Optional[int] = None,
        id_local_destino: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Busca solicitações de declaração de óbito no banco MySQL CSH."""
        # Se nenhuma URL ou sessão for informada ou em modo template, retorna lista vazia
        if not self.session and (not self.database_url or "usuario_csh" in self.database_url or "user:pass@localhost" in self.database_url):
            logger.info("CSH_MYSQL_URL não configurada ou em modo template. Nenhuma consulta externa realizada.")
            return []

        tipo_mat = id_tipo_material or self.id_tipo_material
        local_dest = id_local_destino or self.id_local_destino

        query_sql = self._get_sql_query(
            "obitos_pendentes.sql",
            {
                "limite": limite,
                "id_tipo_material": tipo_mat,
                "id_local_destino": local_dest
            }
        )

        if self.session:
            result = await self.session.execute(text(query_sql))
            rows = result.mappings().all()
            return [dict(r) for r in rows]

        # Conexão assíncrona dinâmica
        engine = create_async_engine(self.database_url, echo=False)
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with async_session() as session:
                result = await session.execute(text(query_sql))
                rows = result.mappings().all()
                return [dict(r) for r in rows]
        finally:
            await engine.dispose()

    async def testar_conexao(self) -> Dict[str, Any]:
        """Testa conectividade direta com o banco CSH e retorna diagnóstico."""
        if not self.database_url:
            return {"status": "erro", "detalhe": "CSH_MYSQL_URL não definida"}

        try:
            engine = create_async_engine(self.database_url, echo=False)
            try:
                async with engine.connect() as conn:
                    val = (await conn.execute(text("SELECT 1"))).scalar()
                return {"status": "sucesso", "resultado": val}
            finally:
                await engine.dispose()
        except Exception as e:
            logger.error(f"Falha ao testar conexão CSH: {e}")
            return {"status": "erro", "detalhe": str(e)}

    async def marcar_obito_notificado(self, id_evento_origem: str) -> bool:
        """Marca o chamado como processado ou registra log (no CSH leitura é read-only por padrão)."""
        logger.info(f"Chamado CSH {id_evento_origem} registrado no fluxo de notificações.")
        return True
