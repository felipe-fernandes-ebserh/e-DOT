import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import text
from src.providers.implementations.obito_mysql_provider import ObitoMySqlProvider

@pytest.mark.asyncio
async def test_obito_mysql_provider_fallback_when_template_url():
    # Quando a URL é default/template, não deve estourar erro, mas sim retornar []
    provider = ObitoMySqlProvider(session=None, database_url="mysql+aiomysql://user:pass@localhost:3306/csh_db")
    obitos = await provider.buscar_obitos_pendentes()
    assert obitos == []
    
    marcado = await provider.marcar_obito_notificado("EVT-1001")
    assert marcado is True

@pytest.mark.asyncio
async def test_obito_mysql_provider_with_injected_session():
    # Simula sessão mockada retornando registros do banco
    mock_session = AsyncMock()
    mock_result = MagicMock()
    
    fake_rows = [
        {
            "id_evento_origem": "CSH-9871",
            "paciente_nome": "JOAO SILVA",
            "paciente_prontuario": "123456",
            "paciente_idade": 65,
            "leito": "10-A",
            "setor_obito": "UTI Geral",
            "data_hora_obito": "2026-10-16 11:30:00",
            "causa_obito": "Choque Séptico",
            "medico_responsavel": "Dr. Carlos",
            "status_notificacao": "PENDENTE"
        }
    ]
    mock_result.mappings.return_value.all.return_value = fake_rows
    mock_session.execute.return_value = mock_result

    provider = ObitoMySqlProvider(session=mock_session)
    res = await provider.buscar_obitos_pendentes(limite=10)
    
    assert len(res) == 1
    assert res[0]["id_evento_origem"] == "CSH-9871"
    assert res[0]["paciente_nome"] == "JOAO SILVA"
    mock_session.execute.assert_called_once()

    # Teste marcar notificado
    marcado = await provider.marcar_obito_notificado("CSH-9871")
    assert marcado is True
