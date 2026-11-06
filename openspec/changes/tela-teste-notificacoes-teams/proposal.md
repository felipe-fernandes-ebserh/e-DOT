# Proposal: Tela de Teste de Notificações e Envio Manual para o Microsoft Teams

## Why

Atualmente, o despacho de mensagens para o Microsoft Teams do e-DOT dispõe de endpoints no backend (`POST /api/notificacoes/teste-teams` e `POST /api/notificacoes/obitos`), mas a equipe da CIHDOTT e a administração não possuem uma interface gráfica dedicada no frontend para validar o canal, simular disparos e verificar como a notificação é renderizada nos smartphones da equipe. Além disso, em cenários de contingência (queda de integração com sistema CSH) ou validação periódica do canal, é indispensável permitir que o operador escolha entre uma mensagem completa (com dados do paciente) ou um alerta de ocorrência simples (sem identificação nominal do paciente), fornecendo formulário para preenchimento ou edição dos dados clínicos antes do envio.

## What Changes

- **Nova Tela no Frontend (`TesteTeams.vue` / `NotificacoesTeste.vue`)**:
  - Interface rica com design system do Framework SETISD (Tailwind CSS, cartões, ícones Heroicons e alertas visuais).
  - Seletor de modo de apresentação: **"Modo Completo (Com dados do paciente)"** vs. **"Modo Alerta Simples (Sem identificação do paciente / Ocorrência imediata)"**.
  - Formulário dinâmico com campos editáveis:
    - Setor / Leito (obrigatório em ambos os modos).
    - Data e Hora do Óbito (preenchido por padrão com a data/hora atual).
    - No Modo Completo: Nome do Paciente, Idade, Sexo, Prontuário, Causa da Morte e indicação de Protocolo de Morte Encefálica (ME).
  - Prévia visual interativa (Preview) simulando a aparência do Adaptive Card no Teams antes do clique de envio.
  - Exibição da lista de destinatários ativos cadastrados que receberão @menções no alerta.
  - Histórico recente dos últimos disparos realizados com status de entrega (`ENTREGUE`, `SIMULADO`, `FALHA_ENVIO`).
- **Navegação no Layout Principal (`DefaultLayout.vue` e `router/index.ts`)**:
  - Novo item de navegação no menu lateral (Sidebar): **"Teste de Notificações"** (ou "Notificações / Teste Teams"), visível para usuários autenticados com privilégio autorizado (`ADMINISTRADOR` ou `COORDENACAO_CIHDOTT`).
  - Nova rota nomeada no Vue Router: `/teste-notificacoes` com meta `requiresAuth: true`.
- **Evolução do Endpoint de Backend (`/api/notificacoes/teste-teams`)**:
  - Permitir opcionalmente o envio de dados customizados preenchidos na tela no corpo da requisição do teste (além do modo), mantendo valores padrão seguros quando omitidos.

## Capabilities

### Modified Capabilities
- `notificacao-obitos`: Extensão do suporte ao teste manual de disparo para aceitar dados clínicos e operacionais parametrizados pela interface web e incorporação de tela dedicada no frontend.

## Impact

- **Frontend (`frontend/src/`)**:
  - Nova view: `frontend/src/views/TesteNotificacoes.vue`.
  - Atualização de rotas em `frontend/src/router/index.ts`.
  - Atualização do menu lateral em `frontend/src/layouts/DefaultLayout.vue`.
  - Integração com `api.ts` e stores (`auth.ts`).
- **Backend (`src/`)**:
  - Pequeno ajuste no schema `TesteTeamsSchema` em `src/routers/notificacao_obitos.py` e controller para aceitar `dados_obito` customizados no teste.
- **Auditoria e Segurança**:
  - Registro de auditoria (`audit_logs`) com categoria `NEGOCIO_CLINICO` ou `CONFIGURACAO` a cada teste disparado com dados manuais.
  - Proteção de acesso na tela e no backend garantindo restrição por perfil (RBAC).
