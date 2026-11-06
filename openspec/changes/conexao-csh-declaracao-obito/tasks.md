# Implementation Tasks

## 1. Configuração e Dependências
- [x] 1.1 Incluir drivers `pymysql` e `asyncmy` no `pyproject.toml`
- [x] 1.2 Implementar normalização de URL MySQL com escape de caracteres especiais na senha em `src/config.py` ou helper dedicado

## 2. SQL Template e Provedor CSH (MySQL)
- [x] 2.1 Atualizar `src/providers/sql/csh/obitos_pendentes.sql` com o `INNER JOIN` entre `chamadomateriais` e `destinochamadomaterial`, filtrando `idTipoMaterial = 12`, `idLocal = 923`, `isAtivo = 1` e `dataCancelamento IS NULL`
- [x] 2.2 Refatorar `src/providers/implementations/obito_mysql_provider.py` para usar a URL normalizada com `asyncmy` e mapear os novos campos

## 3. Rotas de API, Background Polling e Sincronização
- [x] 3.1 Adicionar endpoint de teste e diagnóstico `GET /api/notificacoes/csh/teste-conexao` no roteador `src/routers/notificacao_obitos.py`
- [x] 3.2 Implementar rotina de sincronização de chamados pendentes com prevenção de duplicidade (idempotência via `idChamadoMaterial`)
- [x] 3.3 Implementar serviço de background polling configurável via `.env` (`CSH_POLLING_ATIVO` e `CSH_POLLING_INTERVALO_SEGUNDOS=60`) integrado ao lifespan do FastAPI em `src/main.py`

## 4. Testes Automatizados e Auditoria
- [x] 4.1 Atualizar testes unitários em `tests/test_obito_mysql_provider.py` e criar `tests/test_csh_endpoints.py`
- [x] 4.2 Executar suíte de testes `uv run pytest` e validar conformidade com `python audit_framework.py .`

