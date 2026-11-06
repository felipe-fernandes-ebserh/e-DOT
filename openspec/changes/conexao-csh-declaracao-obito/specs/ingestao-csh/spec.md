# Spec Delta: Ingestão de Chamados CSH para Declaração de Óbito

## ADDED REQUIREMENTS

### REQ-CSH-001: Conectividade Resiliente com Banco CSH
The system MUST support connection to the CSH MySQL database defined in `CSH_MYSQL_URL` handling special characters in passwords (such as `#`) and utilizing the appropriate MySQL driver (`mysql+asyncmy://` for async queries or `mysql+pymysql://` for sync validation).

#### Acceptance Criteria
- Given a valid `CSH_MYSQL_URL` in `.env`, when testing connection or executing queries, the connection MUST succeed without URL parsing errors.
- If `CSH_MYSQL_URL` is unavailable or misconfigured, the provider MUST fail gracefully without crashing the application.

### REQ-CSH-002: Captura de Chamados de Declaração de Óbito
The system MUST query `chamadomateriais` joined with `destinochamadomaterial` filtering for material type `idTipoMaterial = 12` and destination `idLocal = 923` (Triagem Obstétrica).

#### Acceptance Criteria
- Given existing records in `chamadomateriais` with `idTipoMaterial = 12`, `isAtivo = 1`, `dataCancelamento IS NULL` and associated `destinochamadomaterial.idLocal = 923`, the query MUST return these records ordered by `idChamadoMaterial DESC`.
- The returned fields MUST map:
  - `idChamadoMaterial` -> `id_evento_origem`
  - `solicitante` -> `medico_responsavel` / `solicitante`
  - `dataCriacao` -> `data_hora_obito`
  - `obs` -> `observacoes`
  - `ramal` -> `ramal`
  - `idLocal` (923) -> `setor_obito` ("Triagem Obstétrica")
  - `pacienteChamado` -> `paciente_nome` (when available; fallback to "Identificação Pendente / Triagem Obstétrica")

### REQ-CSH-003: Idempotência de Notificação
The system MUST check previously registered notifications in `notificacoes_obitos` using `fonte_origem = 'CSH_MYSQL'` and `id_evento_origem = str(idChamadoMaterial)` to prevent duplicate alerts for the same CSH ticket.

#### Acceptance Criteria
- When a ticket with `idChamadoMaterial` has already been ingested and recorded in `notificacoes_obitos`, subsequent sync executions MUST NOT trigger another alert to Microsoft Teams.

### REQ-CSH-004: Varredura Periódica Automatizada (Background Polling)
The system MUST provide an optional background task that runs at a configurable interval (default: 60s) to poll CSH MySQL for new tickets and dispatch alerts automatically.

#### Acceptance Criteria
- When `CSH_POLLING_ATIVO=true`, the background task MUST wake up every `CSH_POLLING_INTERVALO_SEGUNDOS` seconds.
- The task MUST gracefully handle errors (network drops, DB timeouts) without terminating the server or breaking subsequent polling loops.
- When `CSH_POLLING_ATIVO=false`, the background task MUST NOT run.

### REQ-CSH-005: Endpoint de Diagnóstico e Sincronização Sob Demanda
The system MUST provide authenticated endpoints allowing administrators/coordination to verify connectivity (`GET /api/notificacoes/csh/teste-conexao`) and manually trigger a synchronization run (`POST /api/notificacoes/csh/sincronizar`).

