# Spec Delta

## Purpose

Esta capacidade provê a gestão de perfis e controle de acesso local (RBAC), a administração de destinatários da busca ativa, a formatação adaptativa de alertas com @menções individuais e o despacho resiliente de notificações de óbito hospitalar para o Microsoft Teams da equipe de busca ativa (CIHDOTT).

## ADDED Requirements

### Requirement: Gestão de Perfis de Acesso e Controle RBAC Local
O sistema SHALL manter tabela local de autorização associando logins do Active Directory aos perfis institucionais (ADMINISTRADOR, COORDENACAO_CIHDOTT, EQUIPE_BUSCA_ATIVA, CONSULTA) e DEVE restringir as operações de inclusão, alteração, inativação e exclusão da lista de destinatários exclusivamente a usuários com perfil ADMINISTRADOR ou COORDENACAO_CIHDOTT, rejeitando requisições de outros perfis com código HTTP 403 Forbidden.

#### Scenario: Usuário com perfil de coordenação gerencia destinatários
- **WHEN** um usuário autenticado com perfil COORDENACAO_CIHDOTT realiza alteração na lista de destinatários
- **THEN** o sistema processa a operação com sucesso e grava o registro em trilha de auditoria

#### Scenario: Usuário sem privilégio tenta alterar destinatários
- **WHEN** um usuário com perfil EQUIPE_BUSCA_ATIVA ou CONSULTA tenta incluir ou editar destinatários
- **THEN** o sistema bloqueia a requisição retornando status HTTP 403 Forbidden com mensagem de privilégio insuficiente

### Requirement: Gestão de Destinatários da Equipe de Busca Ativa
O sistema SHALL manter cadastro no banco de dados dos profissionais autorizados da equipe de busca ativa, contendo nome, e-mail institucional corporativo do Microsoft Teams e status ativo/inativo, permitindo incluir, editar e desativar membros sem necessidade de reiniciar a aplicação ou modificar arquivos de configuração.

#### Scenario: Consulta de destinatários ativos para menção
- **WHEN** uma notificação de óbito for preparada para envio
- **THEN** o sistema consulta no banco de dados apenas os membros com status ativo para inclusão na lista de menções do alerta

#### Scenario: Desativação temporária de profissional por motivo de folga
- **WHEN** um profissional é marcado como inativo na gestão de destinatários
- **THEN** o sistema não inclui o nome e a menção desse usuário nas próximas mensagens enviadas ao canal do Teams

### Requirement: Apresentação Adaptativa de Alertas no Microsoft Teams
O sistema SHALL suportar dois modos de apresentação de Adaptive Card no Microsoft Teams: o Modo Completo, com dados clínicos detalhados do paciente quando disponíveis, e o Modo Alerta Simples de Ocorrência, quando o sistema de origem fornecer apenas o evento de óbito com setor e horário, assegurando que o alerta seja entregue imediatamente sem travar esperando cadastros adicionais.

#### Scenario: Disparo em Modo Completo com dados clínicos
- **WHEN** o evento contiver dados de identificação do paciente (nome, idade, causa e leito)
- **THEN** o sistema renderiza o cartão completo destacando os dados clínicos para localização direta

#### Scenario: Disparo em Modo Alerta Simples de Ocorrência
- **WHEN** o evento de óbito for recebido sem os dados clínicos do paciente preenchidos
- **THEN** o sistema renderiza o cartão de alerta simples indicando unidade, leito e horário do óbito, orientando a equipe a iniciar a averiguação presencial imediata

### Requirement: Despacho de Alertas com Menções Individuais no Teams
O sistema SHALL despachar a mensagem para o canal do Microsoft Teams utilizando o padrão Adaptive Cards contendo a tag visual `<at>Nome</at>` no texto e o bloco `msteams.entities` com o e-mail de cada destinatário ativo, assegurando o acionamento de alertas sonoros e notificações push nos smartphones dos membros da equipe.

#### Scenario: Envio com menções individuais bem-sucedido
- **WHEN** o alerta é despachado com destinatários ativos cadastrados
- **THEN** o Microsoft Teams recebe o payload com a lista de entidades de menção e entrega alerta com prioridade nos celulares dos destinatários

#### Scenario: Modo simulado quando webhook não configurado
- **WHEN** a URL do webhook do Teams não estiver preenchida em ambiente de desenvolvimento ou teste
- **THEN** o sistema registra o payload gerado em log e conclui a operação com status de sucesso simulado sem gerar erro de aplicação

### Requirement: Tolerância à Ausência de Prontuário
O sistema SHALL permitir a emissão imediata da notificação mesmo quando o número de prontuário hospitalar estiver indisponível no momento do registro, sinalizando a pendência do número sem bloquear a comunicação de urgência à equipe.

#### Scenario: Disparo com número de prontuário ausente
- **WHEN** um óbito é registrado sem o número de prontuário informado
- **THEN** o sistema gera a notificação destacando o campo de prontuário como "Pendente / Em verificação" e despacha o alerta normalmente

#### Scenario: Disparo com número de prontuário presente
- **WHEN** o número do prontuário é informado no evento
- **THEN** o sistema inclui o número do prontuário formatado no cartão para localização direta no sistema hospitalar

### Requirement: Prevenção de Notificações Duplicadas (Idempotência)
O sistema SHALL garantir idempotência no processamento, utilizando uma chave única de evento baseada no identificador do paciente/óbito para impedir o envio de alertas repetidos para a mesma ocorrência.

#### Scenario: Tentativa de disparo duplicado para mesmo óbito
- **WHEN** uma nova requisição de notificação com a mesma chave de óbito já processada for recebida
- **THEN** o sistema identifica a duplicidade, não envia nova mensagem ao Microsoft Teams e retorna o status da notificação original já existente

#### Scenario: Novo óbito de paciente distinto
- **WHEN** uma requisição com identificador inédito é submetida
- **THEN** o sistema cria um novo registro de notificação e procede com o envio

### Requirement: Resiliência e Tratamento de Falhas de Envio
O sistema SHALL capturar erros de rede, indisponibilidade ou respostas de erro da API do Microsoft Teams, executando retentativas automáticas com espaçamento exponencial até o limite configurado antes de classificar a entrega como falha.

#### Scenario: Falha transitória de conectividade com reenvio bem-sucedido
- **WHEN** a primeira tentativa de envio ao Teams falhar por timeout ou erro 5xx
- **THEN** o sistema agenda nova tentativa automática com backoff exponencial e atualiza o registro para enviado ao obter sucesso

#### Scenario: Esgotamento de tentativas de reenvio
- **WHEN** todas as tentativas configuradas falharem consecutivamente
- **THEN** o sistema marca o registro com status de "Falha no Envio", registra os detalhes do erro e gera alerta administrativo interno

### Requirement: Ingestão de Óbitos via Base MySQL do Sistema CSH
O sistema SHALL suportar a leitura assíncrona de eventos de óbito a partir da base de dados MySQL do sistema CSH através de um provedor de dados desacoplado, permitindo acoplar a consulta SQL final assim que o campo de gatilho/trigger de óbito for formalmente homologado.

#### Scenario: Leitura de novos óbitos no banco CSH
- **WHEN** novos registros com status de óbito forem inseridos na base MySQL do CSH
- **THEN** o provedor de dados extrai os registros inéditos e os encaminha para a fila de formatação e despacho

#### Scenario: Execução em modo contingência / manual
- **WHEN** a integração com a base CSH estiver inoperante ou antes da definição da trigger definitiva
- **THEN** o sistema permite a inserção manual de óbitos via API protegida sem interromper o serviço de notificações

### Requirement: Trilha de Auditoria e Conformidade de Dados
O sistema SHALL registrar em trilha de auditoria imutável (`audit_logs`) cada operação de alteração de perfis de usuários, modificação de destinatários, disparo de alertas e resposta do webhook do Teams, contendo login do operador, IP de origem, timestamp e estado antes/depois da alteração conforme a LGPD e o padrão do HC-UFPE.

#### Scenario: Auditoria de alteração de perfil de usuário
- **WHEN** um administrador concede ou revoga o perfil de coordenação de um usuário
- **THEN** o sistema grava um log categorizado como "SEGURANCA" contendo os dados anteriores e novos

#### Scenario: Auditoria de disparo de notificação
- **WHEN** uma notificação de óbito for enviada ao Teams
- **THEN** o sistema grava um log categorizado como "NEGOCIO_CLINICO" registrando a entrega aos destinatários
