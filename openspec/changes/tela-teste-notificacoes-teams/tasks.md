# Tasks: Tela de Teste de Notificações e Envio Manual Teams

## 1. Backend: Extensão do Endpoint de Teste

- [x] 1.1 Atualizar `TesteTeamsSchema` em `src/routers/notificacao_obitos.py` para aceitar `dados_obito: Optional[Dict[str, Any]] = None`
- [x] 1.2 Atualizar o método `disparar_teste_teams` em `src/controllers/notificacao_obito_controller.py` para mesclar dados customizados recebidos com os padrões de teste
- [x] 1.3 Adicionar testes em `tests/test_router_notificacao_obitos.py` validando o envio de teste com dados customizados e verificar com `pytest`

## 2. Frontend: Roteamento e Menu Lateral

- [x] 2.1 Adicionar rota `/teste-notificacoes` em `frontend/src/router/index.ts` apontando para `TesteNotificacoes.vue` com `meta: { requiresAuth: true }`
- [x] 2.2 Adicionar item no menu lateral em `frontend/src/layouts/DefaultLayout.vue` com ícone `BellAlertIcon` e verificação de privilégio (`isAdmin || isCoordenacao`)

## 3. Frontend: Componente de Tela de Teste (`TesteNotificacoes.vue`)

- [x] 3.1 Criar a view `frontend/src/views/TesteNotificacoes.vue` com cabeçalho de página e resumo da finalidade
- [x] 3.2 Implementar o seletor interativo de modo: **"Modo Completo"** vs. **"Modo Alerta Simples"**
- [x] 3.3 Implementar o formulário reativo com campos editáveis e preenchimento de valores padrão de exemplo
- [x] 3.4 Implementar a caixa de prévia em tempo real (Card Preview) simulando o Adaptive Card do Teams
- [x] 3.5 Integrar a chamada de envio via API `api.post('/notificacoes/teste-teams', payload)` com feedback visual (Toast/Alert) e botão com estado de carregamento
- [x] 3.6 Exibir a lista de destinatários ativos que receberão menção na notificação
- [x] 3.7 Adicionar tabela com histórico dos disparos de teste realizados na sessão

## 4. Testes e Validação de Conformidade

- [x] 4.1 Validar compilação do frontend TypeScript e Vue (`npm run build` ou checagem de tipos)
- [x] 4.2 Executar testes automatizados do backend com `pytest`
- [x] 4.3 Executar auditor do framework com `python audit_framework.py .` garantindo 100% de conformidade
