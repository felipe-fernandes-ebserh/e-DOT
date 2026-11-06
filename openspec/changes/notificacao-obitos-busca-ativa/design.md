# Technical Design: Notificação de Óbitos para Busca Ativa via Microsoft Teams

## Context

O projeto e-DOT adota o padrão arquitetural do Framework-SETISD-HC-UFPE (`FastAPI` assíncrono no backend, `Vue 3 + Vite` no frontend, persistência híbrida via `SQLAlchemy 2.0` com PostgreSQL/SQLite, e autenticação AD/LDAP). Atualmente, a busca ativa de potenciais doadores depende de contato informal ou busca presencial em leitos e UTIs.

Para atender à necessidade prioritária da equipe de acolhimento e busca ativa (CIHDOTT) e contornar a pendência na definição do campo de trigger na base MySQL do sistema CSH, o desenvolvimento foi estruturado com foco em duas entregas:
- **Fase 1 (Imediata)**: 
  - Criação da governança de usuários e perfis locais (RBAC) com pré-validação no Active Directory.
  - Tabela de gestão de destinatários da busca ativa com controle de acesso estrito.
  - Motor de montagem de Adaptive Cards com suporte a dois modos (Completo vs. Alerta de Ocorrência Simples) e @menções individuais para forçar notificações push/sonoras nos celulares.
  - Endpoints de teste e disparo manual protegido.
- **Fase 2 (Após definição da trigger)**: 
  - Conector `ObitoMySqlProvider` para leitura automática da base MySQL do sistema CSH.

Ver `proposal.md` para motivação e justificativa negocial; ver `specs/notificacao-obitos/spec.md` para os requisitos normativos de comportamento.

## Goals / Non-Goals

**Goals:**
- Implementar modelo de autorização local (RBAC) no banco da aplicação com os perfis: `ADMINISTRADOR`, `COORDENACAO_CIHDOTT`, `EQUIPE_BUSCA_ATIVA` e `CONSULTA`.
- Proteger as rotas de manutenção de destinatários (`POST/PUT/DELETE /api/notificacoes/destinatarios`) para que apenas usuários com perfil `ADMINISTRADOR` ou `COORDENACAO_CIHDOTT` possam alterar quem recebe alertas.
- Suportar apresentação adaptativa em Adaptive Cards:
  - *Modo Completo*: Dados clínicos do paciente (nome, idade, causa, leito, prontuário).
  - *Modo Alerta Simples*: Alerta de ocorrência imediata (unidade, leito vago por óbito, horário) quando o CSH ainda não tiver registrado o paciente.
- Garantir a marcação de `<at>Nome</at>` no texto e o bloco `msteams.entities` com os e-mails institucionais dos membros ativos.
- Suportar modo MOCK quando a variável `TEAMS_WEBHOOK_URL` ainda não estiver configurada.
- Assegurar 100% de conformidade com as diretrizes do `AGENTS.md` (Security Headers, Default-Private Routers, Governança de Configurações, Audit Logs e Pytest).

**Non-Goals:**
- Não permitir autodesignação de privilégios de coordenação sem validação de administrador.
- Não expor dados clínicos na mensagem se a notificação for emitida em modo de alerta simples de ocorrência.
- Não substituir o prontuário eletrônico hospitalar ou a declaração oficial de óbito.

## Decisions

### 1. Modelo de Autorização Local (RBAC) e Usuários (`usuarios`)
- **Decisão**: Criar a tabela `usuarios` no banco SQLite da aplicação:
  ```python
  class UsuarioSistema(Base):
      __tablename__ = "usuarios"
      id = Column(Integer, primary_key=True, autoincrement=True)
      username = Column(String(80), unique=True, nullable=False, index=True) # Login AD (ex: joao.silva)
      nome = Column(String(150), nullable=False)
      email = Column(String(150), nullable=False)
      departamento = Column(String(100), nullable=True)
      perfil = Column(String(50), nullable=False, default="CONSULTA") # ADMINISTRADOR, COORDENACAO_CIHDOTT, EQUIPE_BUSCA_ATIVA, CONSULTA
      ativo = Column(Boolean, default=True, nullable=False)
      data_criacao = Column(DateTime, default=datetime.utcnow)
      data_atualizacao = Column(DateTime, onupdate=datetime.utcnow)
  ```
- **Racional**:
  - Respeita o padrão de segurança em 2 etapas do Framework-SETISD: a autenticação de senha é feita no AD corporativo (`EBSERHNET`), mas a autorização de papéis na aplicação fica na tabela local.
  - Permite à chefia da CIHDOTT usar o botão "Consultar AD" (`GET /api/admin/ad-user-search/{username}`) para localizar o profissional e conceder o perfil.

### 2. Dependência de Segurança e Proteção RBAC
- **Decisão**: Implementar a dependência FastAPI:
  ```python
  async def verify_coordenacao_or_admin(
      current_user: dict = Depends(auth_handler.decode_token),
      db: AsyncSession = Depends(get_app_db_session)
  ):
      username = current_user.get("username")
      # Verifica se é admin geral do AD
      if "GLO-SEC-HCPE-SETISD" in current_user.get("groups", []):
          return current_user
      
      # Consulta perfil na tabela local
      stmt = select(UsuarioSistema).where(UsuarioSistema.username == username, UsuarioSistema.ativo == True)
      user_obj = (await db.execute(stmt)).scalar_one_or_none()
      if not user_obj or user_obj.perfil not in ["ADMINISTRADOR", "COORDENACAO_CIHDOTT"]:
          raise HTTPException(
              status_code=status.HTTP_403_FORBIDDEN,
              detail="Acesso restrito à Coordenação da CIHDOTT e Administradores."
          )
      return user_obj
  ```
- **Racional**:
  - Protege com rigor os métodos de mutação da lista de destinatários, garantindo que usuários comuns da equipe ou curiosos não alterem quem recebe os alertas.

### 3. Apresentação Adaptativa do Adaptive Card (Modo Completo vs. Modo Simples)
- **Decisão**: O gerador de cartões (`teams_card_helper.py`) inspeciona o objeto de óbito recebido e seleciona o template:
  - **Template A (Completo)**: Usado quando `nome_paciente` está presente. Renderiza os fatos: Paciente, Idade, Causa, Leito/Setor e Prontuário.
  - **Template B (Alerta Simples)**: Usado quando `nome_paciente` for nulo ou não informado. Renderiza título "🚨 ALERTA DE ÓBITO HOSPITALAR", exibe Setor/Unidade, Leito e Data/Hora, com nota em destaque: *"Dados do paciente pendentes no sistema de origem. Iniciar averiguação presencial da busca ativa no setor."*
- **Racional**:
  - Blinda a aplicação contra atrasos de preenchimento no CSH e atende a eventuais restrições de privacidade da informação.

### 4. Gestão de Destinatários e Menções Individuais (`msteams.entities`)
- **Decisão**: Tabela local `destinatarios_notificacao`:
  ```python
  class DestinatarioNotificacao(Base):
      __tablename__ = "destinatarios_notificacao"
      id = Column(Integer, primary_key=True, autoincrement=True)
      nome = Column(String(150), nullable=False)
      email_teams = Column(String(150), nullable=False, unique=True)
      cargo_setor = Column(String(100), nullable=True)
      ativo = Column(Boolean, default=True, nullable=False)
      data_criacao = Column(DateTime, default=datetime.utcnow)
  ```
  O payload enviado ao Teams anexa no bloco `msteams.entities` todos os membros com `ativo = True`.

### 5. Ingestão Desacoplada para MySQL (Sistema CSH - Fase 2)
- **Decisão**:
  - Interface `ObitoProviderInterface` e conector `ObitoMySqlProvider`.
  - Template SQL externo em `src/providers/sql/csh/obitos_pendentes.sql`.
  - Quando a equipe do CSH definir o campo de trigger (ex: flag de óbito ou status de leito), apenas o arquivo `.sql` é atualizado.

## Risks / Trade-offs

- **[Risco: Usuário tenta acessar funcionalidade administrativa sem cadastro local prévio]**
  → *Mitigação*: Retorno HTTP 403 amigável informando que o usuário precisa ser cadastrado pela coordenação; usuários administradores padrão do AD (`GLO-SEC-HCPE-SETISD`) mantêm acesso mestre imediato para configuração inicial.
- **[Risco: Notificação em Modo Simples gerar deslocamento desnecessário]**
  → *Mitigação*: A mensagem simples indica claramente a unidade e o leito vago por óbito, permitindo que a equipe priorize a visita no setor correto.

## Migration Plan

1. **Alembic**: Criar migração gerando:
   - `usuarios`
   - `destinatarios_notificacao`
   - `notificacoes_obitos`
2. **Carga Inicial (Seed)**: Criar usuário padrão inicial de desenvolvimento / homologação (`admin`).
3. **Variáveis de Ambiente**:
   - `TEAMS_WEBHOOK_URL`
   - `TEAMS_NOTIFICACOES_ATIVO`
   - `CSH_MYSQL_URL` (para a Fase 2)

## Open Questions

- **Q1 (Sistema CSH)**: Qual é a tabela e coluna definitiva do CSH que indicará o óbito? (Abordado na Fase 2).
