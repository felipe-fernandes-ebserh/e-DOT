# Proposal: Notificação de Óbitos para Busca Ativa via Microsoft Teams

## Why

A comunicação de óbitos hospitalares à equipe de busca ativa e acolhimento familiar (CIHDOTT) atualmente ocorre de forma fragmentada e manual (ligações, mensagens descentralizadas de WhatsApp ou rondas físicas), fazendo com que a equipe frequentemente só tome conhecimento de um óbito quando o corpo já está sendo liberado, inviabilizando o acolhimento oportuno da família e os protocolos de doação de órgãos e tecidos. Com a definição do Microsoft Teams como canal corporativo oficial com entrega de alertas nos celulares da equipe em trânsito, é necessário estabelecer uma capacidade automatizada, rápida e auditável de disparo de alertas com menções individuais (@mentions) para despertar alertas sonoros e push nos celulares dos profissionais, com governança de perfis de acesso e flexibilidade para notificações completas ou alertas simples de ocorrência.

## What Changes

- **Motor de Disparo com @Menções Individuais (Fase 1 - Prioridade)**: Envio de cartões ricos (Adaptive Cards) para canal do Microsoft Teams contendo marcação individualizada (`<at>Nome</at>` via `msteams.entities`) de cada profissional da equipe, garantindo notificações sonoras e push nos smartphones.
- **Apresentação Adaptativa (Modo Completo vs. Alerta Simples)**: Suporte a envio de dados clínicos detalhados do paciente quando disponíveis pelo CSH, ou disparo imediato de alerta de ocorrência (notificação de óbito no setor/horário para busca presencial) caso os dados do paciente ainda não estejam consolidados no sistema de origem.
- **Gestão de Perfis de Acesso e Destinatários (RBAC Local)**:
  - Tabela local de usuários do sistema integrada ao login do AD (Ebserh), com perfis definidos (`ADMINISTRADOR`, `COORDENACAO_CIHDOTT`, `EQUIPE_BUSCA_ATIVA`, `CONSULTA`).
  - Restrição de gerenciamento da lista de destinatários do Teams exclusivamente para a coordenação da CIHDOTT e administradores, impedindo edições por usuários não autorizados (HTTP 403).
  - Pré-validação de novos usuários via consulta ao Active Directory.
- **Endpoint de Teste e Disparo de Contingência**: Rota de API protegida para simulação e teste de disparo de alertas ao Teams com dados fictícios ou registro manual de óbitos.
- **Ingestão via MySQL / Sistema CSH (Fase 2)**: Conexão com o banco de dados MySQL alimentado pelo sistema CSH, desacoplando a leitura de dados da definição do campo de trigger de óbito que ainda está em validação.
- **Rastreabilidade, Resiliência e Auditoria**: Registro imutável de cada tentativa de disparo, alteração de permissões e destinatários (`audit_logs`), com conformidade com a LGPD e governança hospitalar (Framework SETISD HC-UFPE).

## Capabilities

### New Capabilities
- `notificacao-obitos`: Gestão de usuários e permissões locais (RBAC), controle de destinatários da busca ativa, formatação adaptativa de alertas (completo vs. ocorrência simples) com @menções individuais, despacho resiliente para o Microsoft Teams e conector de ingestão para MySQL/CSH.

### Modified Capabilities
<!-- Nenhuma capacidade existente alterada (projeto greenfield no módulo de notificações) -->

## Impact

- **Backend (`src/`)**:
  - Novos modelos: `UsuarioSistema`, `DestinatarioNotificacao` e `NotificacaoObito` em `src/models/`.
  - Migrações Alembic para as tabelas `usuarios`, `destinatarios_notificacao` e `notificacoes_obitos`.
  - Controle de acesso (RBAC) via dependências FastAPI (`verify_coordenacao_or_admin`).
  - Serviço de montagem de Adaptive Cards com suporte a modo completo e modo simples de ocorrência.
  - Conector assíncrono para o banco MySQL do CSH (`ObitoMySqlProvider`).
  - Rotas de API em `src/routers/notificacao_obitos.py` e `src/routers/usuarios.py`.
- **Configurações e Variáveis de Ambiente**:
  - `TEAMS_WEBHOOK_URL`: URL do Webhook do canal (com fallback simulado para testes).
  - `TEAMS_NOTIFICACOES_ATIVO`: Flag booleano de habilitação geral.
  - `CSH_MYSQL_URL`: DSN de conexão com o banco MySQL do sistema CSH.
- **Sistemas Externos**:
  - Microsoft Teams (recebimento de webhooks/cards com @menções).
  - Active Directory (validação de credenciais e busca de usuários).
  - Banco de Dados MySQL do CSH (leitura de óbitos).
