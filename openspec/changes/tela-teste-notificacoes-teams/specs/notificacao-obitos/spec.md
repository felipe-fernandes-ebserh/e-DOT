# Spec Delta: Tela de Teste de Notificações e Envio Manual Teams

## Purpose

Esta modificação expande a capacidade `notificacao-obitos` adicionando uma interface visual dedicada no frontend Vue 3 para teste e disparo de notificações para o Microsoft Teams, permitindo ao usuário alternar entre o Modo Completo (com dados do paciente) e o Modo Alerta Simples (sem identificação nominal), além de preencher ou customizar todos os campos da ocorrência antes do envio.

## ADDED Requirements

### Requirement: Interface Web de Teste de Disparo ao Teams
O sistema SHALL fornecer uma tela dedicada no frontend (`/teste-notificacoes`) acessível aos perfis autorizados (`ADMINISTRADOR`, `COORDENACAO_CIHDOTT`), permitindo parametrizar e despachar alertas diretamente ao canal ou grupo do Microsoft Teams configurado.

#### Scenario: Operador acessa a tela de teste de notificações
- **GIVEN** que o usuário está autenticado com perfil `ADMINISTRADOR` ou `COORDENACAO_CIHDOTT`
- **WHEN** acessa a rota `/teste-notificacoes` pelo menu lateral
- **THEN** o sistema exibe o formulário de disparo, a lista de destinatários ativos que receberão menção e o histórico dos últimos disparos

#### Scenario: Usuário sem privilégio tenta acessar a tela
- **GIVEN** que o usuário está autenticado com perfil de apenas consulta ou equipe básica
- **WHEN** tenta navegar para `/teste-notificacoes`
- **THEN** a interface oculta o item no menu lateral e exibe aviso de permissão insuficiente se acessado via URL direta

---

### Requirement: Seletor de Modo de Apresentação (Completo vs. Alerta Simples)
A tela de teste SHALL conter um seletor visual em destaque permitindo alternar dinamicamente entre **Modo Completo** (com dados clínicos do paciente) e **Modo Alerta Simples** (ocorrência imediata sem identificação do paciente), adaptando instantaneamente os campos exibidos no formulário.

#### Scenario: Seleção do Modo Alerta Simples
- **WHEN** o usuário seleciona a opção "Modo Alerta Simples (Sem identificação do paciente)"
- **THEN** os campos de Nome do Paciente, Idade, Sexo e Prontuário são desabilitados ou ocultados, mantendo ativos apenas Setor/Leito e Data/Hora da ocorrência

#### Scenario: Seleção do Modo Completo
- **WHEN** o usuário seleciona a opção "Modo Completo (Com dados do paciente)"
- **THEN** os campos clínicos (Nome, Idade, Sexo, Prontuário, Causa da Morte, Protocolo de ME) tornam-se visíveis e editáveis

---

### Requirement: Edição e Parametrização de Dados do Óbito
A interface SHALL disponibilizar campos editáveis preenchidos previamente com valores padrão de exemplo/teste, permitindo ao operador alterar quaisquer informações (nome, leito, causa de óbito, prontuário) antes de confirmar o disparo.

#### Scenario: Customização dos dados e envio com sucesso
- **WHEN** o operador preenche um leito específico e altera a causa de morte no formulário e clica em "Disparar Alerta de Teste"
- **THEN** o frontend envia a requisição contendo esses dados para a API, que formata o Adaptive Card com as informações preenchidas e entrega ao Teams
- **AND** a tela exibe feedback de sucesso com o status retornado (`200/202`), inserindo o evento no histórico local

---

### Requirement: Prévia Visual do Cartão Adaptativo (Preview)
A interface SHALL exibir em tempo real uma prévia visual simulando o layout do cartão adaptativo do Teams (cabeçalho de alerta, cores de aviso, menções e tabela de dados) de acordo com o modo selecionado e os campos preenchidos.

#### Scenario: Atualização em tempo real da prévia
- **WHEN** o operador digita no campo "Setor/Leito"
- **THEN** a caixa de prévia visual do cartão reflete imediatamente o novo texto informado
