# Tasks: Notificação de Óbitos para Busca Ativa via Microsoft Teams

## 1. Configuração e Modelos de Banco de Dados

- [x] 1.1 Atualizar `src/config.py` e `.env.example` com as variáveis do Teams (`TEAMS_WEBHOOK_URL`, `TEAMS_NOTIFICACOES_ATIVO`, `NOTIFICACOES_MAX_RETENTATIVAS`) e verificar inicialização sem erros
- [x] 1.2 Criar modelo `UsuarioSistema` em `src/models/usuario.py` contendo login AD, nome, e-mail, perfil e status ativo
- [x] 1.3 Criar modelo `DestinatarioNotificacao` em `src/models/destinatario_notificacao.py` para armazenar nome, e-mail institucional do Teams e status ativo
- [x] 1.4 Criar modelo `NotificacaoObito` em `src/models/notificacao_obito.py` contendo dados clínicos mínimos, histórico de destinatários e unicidade composta para idempotência
- [x] 1.5 Criar migração Alembic gerando as tabelas `usuarios`, `destinatarios_notificacao` e `notificacoes_obitos` e verificar execução com `alembic upgrade head`
- [x] 1.6 Escrever testes unitários em `tests/test_models_notificacao.py` validando os modelos e restrições de unicidade com `pytest`

## 2. Motor de Formatação Adaptativo e Envio ao Microsoft Teams (Fase 1)

- [x] 2.1 Implementar construtor de Adaptive Cards em `src/helpers/teams_card_helper.py` suportando Modo Completo (dados clínicos) e Modo Alerta Simples (apenas evento/setor/horário), incluindo menções individuais em `msteams.entities`
- [x] 2.2 Implementar serviço de envio `TeamsService` em `src/services/teams_service.py` com suporte a modo MOCK (quando a URL não estiver configurada) e retentativas exponenciais via `httpx`
- [x] 2.3 Escrever testes unitários em `tests/test_teams_service.py` validando Modo Completo, Modo Simples, menções nominais e modo mock com `pytest`

## 3. Controle de Acesso (RBAC) e Gestão da Equipe (Fase 1)

- [x] 3.1 Implementar dependência de autorização `verify_coordenacao_or_admin` em `src/dependencies.py` validando se o usuário possui perfil autorizado na tabela local ou grupo mestre do AD
- [x] 3.2 Implementar `UsuarioController` em `src/controllers/usuario_controller.py` com endpoints para listar e atribuir perfis a usuários consultados do AD, registrando auditoria via `audit_helper`
- [x] 3.3 Implementar `DestinatarioController` em `src/controllers/destinatario_controller.py` para manutenção da lista de profissionais da busca ativa, restrito à coordenação e administradores
- [x] 3.4 Escrever testes de segurança em `tests/test_rbac_destinatarios.py` verificando bloqueio HTTP 403 para usuários comuns e sucesso para usuários de coordenação com `pytest`

## 4. Endpoints de Notificação e Disparo de Teste (Fase 1)

- [x] 4.1 Implementar `NotificacaoObitoController` em `src/controllers/notificacao_obito_controller.py` coordenando busca de destinatários ativos, montagem do card adaptativo, despacho e gravação do histórico
- [x] 4.2 Criar roteador `src/routers/notificacao_obitos.py` protegido com `Depends(auth_handler.decode_token)` disponibilizando CRUD de destinatários e endpoint de teste `POST /api/notificacoes/teste-teams`
- [x] 4.3 Registrar os novos roteadores em `src/main.py`
- [x] 4.4 Escrever testes de API em `tests/test_router_notificacao_obitos.py` testando disparo de teste em Modo Completo e Modo Simples com `pytest`

## 5. Camada de Ingestão Desacoplada para MySQL / Sistema CSH (Fase 2)

- [x] 5.1 Criar interface `ObitoProviderInterface` em `src/providers/interfaces/obito_provider_interface.py` e template SQL em `src/providers/sql/csh/obitos_pendentes.sql`
- [x] 5.2 Implementar `ObitoMySqlProvider` em `src/providers/implementations/obito_mysql_provider.py` gerenciando conexão assíncrona ao banco MySQL do CSH
- [x] 5.3 Escrever testes automatizados para o conector em `tests/test_obito_mysql_provider.py` com mocks de banco de dados e verificar com `pytest`

## 6. Verificação de Conformidade e Auditoria Final

- [x] 6.1 Executar a suíte de auditoria do hospital `python audit_framework.py .` e verificar 100% de conformidade nos 11 pilares
- [x] 6.2 Executar a suíte completa de testes com `pytest` e verificar aprovação sem falhas

## Workflow follow-up

- Cadastrar os usuários com perfil `COORDENACAO_CIHDOTT` utilizando o botão de consulta ao AD.
- Cadastrar os nomes e e-mails corporativos da equipe de busca ativa na lista de destinatários.
- Obter a URL do Webhook do canal no Microsoft Teams e atualizar no `.env`.
- Realizar teste de disparo e validar alertas push sonoros no celular em Modo Completo e Modo Simples.
- Definir junto à equipe do sistema CSH o campo exato de trigger no MySQL e conectar o provider da Fase 2.
- Executar `openspec archive` após homologação da mudança.
