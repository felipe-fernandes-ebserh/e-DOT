# Proposal: Conexão CSH para Captura de Eventos de Solicitação de Declaração de Óbito

## Why

A equipe da CIHDOTT / Busca Ativa do HC-UFPE necessita de agilidade máxima ao tomar conhecimento de novos óbitos hospitalares para realizar o acolhimento familiar em tempo hábil e conduzir os protocolos de doação de órgãos e tecidos. No sistema CSH (Central de Serviços do Hospital), o fluxo de solicitação de entrega da Declaração de Óbito (DO) gera registros operacionais nas tabelas de materiais. A identificação desses eventos em tempo real substitui a busca manual, garantindo que assim que uma solicitação de DO for aberta no CSH (inicialmente com destino à Triagem Obstétrica), a equipe de busca ativa seja alertada automaticamente via Microsoft Teams.

## What Changes

- **Integração Real com o Banco MySQL CSH (Homologação / Produção)**:
  - Tratamento adequado da URL de conexão (`CSH_MYSQL_URL`), incluindo suporte a caracteres especiais na senha (ex: `#`) via URL encoding e adoção dos drivers assíncronos/síncronos (`asyncmy` / `pymysql`).
  - Atualização do template SQL em `src/providers/sql/csh/obitos_pendentes.sql` para consultar a estrutura real do CSH:
    - Tabela de origem: `chamadomateriais cm`
    - Junção com destino: `INNER JOIN destinochamadomaterial dcm ON dcm.idChamadoMaterial = cm.idChamadoMaterial`
    - Filtro de Tipo de Material: `cm.idTipoMaterial = 12` (Solicitação de Declaração de Óbito)
    - Filtro de Destino: `dcm.idLocal = 923` (Triagem Obstétrica)
    - Filtro de status ativo: `cm.isAtivo = 1` e `cm.dataCancelamento IS NULL`
  - Mapeamento dos campos do chamado (`idChamadoMaterial`, `solicitante`, `dataCriacao`, `ramal`, `obs`, `pacienteChamado`) para o schema interno de eventos de óbito / notificação.
- **Rastreabilidade e Idempotência de Ingestão**:
  - Utilização de `idChamadoMaterial` como `id_evento_origem` no banco local `data/app.db` (`notificacoes_obitos`) com restrição única composta (`fonte_origem` + `id_evento_origem`) para garantir que nenhum chamado do CSH seja notificado mais de uma vez.
- **Varredura Periódica Automatizada (Background Polling Task)**:
  - Criação de uma tarefa em background assíncrona gerenciada no ciclo de vida da aplicação (`lifespan` do FastAPI).
  - Parametrização via `.env`:
    - `CSH_POLLING_ATIVO=true` (habilitação da rotina automática).
    - `CSH_POLLING_INTERVALO_SEGUNDOS=60` (intervalo configurável, padrão 60 segundos).
  - Execução segura: a cada ciclo busca os chamados pendentes, verifica a idempotência no banco local, dispara os alertas no Microsoft Teams com as @menções dos profissionais e persiste o registro.
- **Serviço de Diagnóstico e Disparo Manual**:
  - Endpoint de teste de diagnóstico de conexão com o banco CSH (`GET /api/notificacoes/csh/teste-conexao`).
  - Endpoint de sincronização manual sob demanda (`POST /api/notificacoes/csh/sincronizar`).

## Capabilities

### New Capabilities
- `ingestao-csh-declaracao-obito`: Integração do conector `ObitoMySqlProvider` com o banco real do CSH para extração contínua e segura de chamados de material do tipo DO (idTipoMaterial=12) direcionados aos setores monitorados (ex: idLocal=923).

### Modified Capabilities
- `notificacao-obitos`: Atualização do fluxo de ingestão e dos esquemas de dados de evento para consumir campos reais provenientes do CSH.

## Impact

- **Backend (`src/`)**:
  - `src/config.py`: Sanitização e parsing robusto da `CSH_MYSQL_URL` com driver `mysql+asyncmy` ou `mysql+pymysql`.
  - `src/providers/implementations/obito_mysql_provider.py`: Atualização da leitura dos registros reais do CSH.
  - `src/providers/sql/csh/obitos_pendentes.sql`: Query ajustada para `chamadomateriais` e `destinochamadomaterial`.
  - `src/routers/notificacao_obitos.py`: Adição de endpoint de status de conectividade e captura do CSH.
- **Dependências**:
  - Adição de `asyncmy` e `pymysql` no `pyproject.toml` para comunicação com MySQL.

