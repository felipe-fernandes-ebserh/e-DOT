# Technical Design: Tela de Teste de Notificações e Envio Manual Teams

## Context

O backend do e-DOT já possui infraestrutura robusta para criação e despacho de Adaptive Cards para o Microsoft Teams (`TeamsService` e `teams_card_helper.py`), além de tabelas para destinatários e logs de auditoria. No entanto, o frontend atual (`frontend/src/views/`) não possui interface para interagir com o endpoint de testes, limitando a validação a chamadas de terminal ou scripts manuais.

Esta solução cria a tela completa de teste no frontend com base nos padrões do Framework SETISD HC-UFPE, integrando a navegação do sistema, o controle RBAC e permitindo parametrização dos dados.

## Goals / Non-Goals

**Goals:**
- Criar a view `frontend/src/views/TesteNotificacoes.vue` rica e intuitiva.
- Adicionar o seletor em abas/cards tipo rádio:
  - *Modo Completo* (com dados do paciente).
  - *Modo Alerta Simples* (somente setor/horário, sem dados de identificação).
- Permitir edição dinâmica dos campos com valores padrão de teste e validação de campos mínimos (ex: setor/leito).
- Implementar um componente de *Card Preview* que renderiza uma miniatura fiel do Adaptive Card que será enviado ao Teams.
- Exibir os destinatários cadastrados que serão @mencionados no alerta.
- Atualizar a barra de navegação lateral (`DefaultLayout.vue`) e o roteador Vue (`router/index.ts`).
- Atualizar o endpoint do backend `POST /api/notificacoes/teste-teams` para aceitar um objeto `dados_obito` opcional no corpo da requisição.

**Non-Goals:**
- Não alterar a lógica de background polling de ingestão automática (CSH/MySQL).
- Não persistir notificações de teste como óbitos oficiais no prontuário de pacientes.

## Decisions

### 1. Evolução do Schema de Teste no Backend
- **Decisão**: Atualizar `TesteTeamsSchema` em `src/routers/notificacao_obitos.py`:
  ```python
  class TesteTeamsSchema(BaseModel):
      modo: str = Field(default="COMPLETO", description="Modo do teste: 'COMPLETO' ou 'ALERTA_SIMPLES'")
      dados_obito: Optional[Dict[str, Any]] = Field(default=None, description="Dados customizados para o teste")
  ```
- **Racional**: Permite que o teste continue funcionando como antes (apenas com `{"modo": "COMPLETO"}` gerando dados aleatórios/fictícios), mas se o frontend enviar o payload customizado preenchido pelo usuário, o `NotificacaoObitoController.disparar_teste_teams` utiliza esses dados.

### 2. Estrutura da View Vue 3 (`TesteNotificacoes.vue`)
- **Seletor de Modo**:
  - Dois cards clicáveis com borda em destaque (`border-primary-500` quando ativo, ícone de documento completo vs. sino de alerta rápido).
- **Formulário Reativo**:
  ```typescript
  interface FormTeste {
    modo: 'COMPLETO' | 'ALERTA_SIMPLES';
    setor_leito: string;
    data_hora_obito: string;
    // Campos do modo completo
    nome_paciente: string;
    idade: number | null;
    sexo: string;
    prontuario: string;
    causa_morte: string;
    protocolo_me: boolean;
  }
  ```
- **Prévia Visual (Preview)**:
  - Quadro com estilo visual imitando o Microsoft Teams (fundo cinza suave, card branco com cabeçalho em vermelho carmesim hospitalar, menções em azul e tabela de propriedades).
- **Histórico e Status**:
  - Tabela com os últimos testes disparados na sessão com indicação visual de status (`Entregue`, `Simulado`, `Falha`).

### 3. Integração com Layout e Permissões
- Adicionar no menu lateral:
  ```html
  <router-link
    v-if="authStore.isAuthenticated && (authStore.isAdmin || authStore.isCoordenacao)"
    to="/teste-notificacoes"
    ...
  >
    <BellAlertIcon class="h-6 w-6 shrink-0" />
    <span v-if="!isCollapsed">Teste Teams</span>
  </router-link>
  ```
- Configurar rota no `router/index.ts` com `meta: { requiresAuth: true }`.

## Risks & Mitigations

- **Risco**: Usuário disparar múltiplos testes seguidos e poluir o grupo corporativo do Teams.
  - **Mitigação**: Botão com estado de carregamento (`loading`), desabilitado durante o envio e mensagem de confirmação/alerta visual de que a mensagem será entregue no grupo real configurado.
- **Risco**: Usuário sem perfil de coordenação tentar disparar o teste pela API.
  - **Mitigação**: O endpoint já é blindado com `Depends(verify_coordenacao_or_admin)`.
