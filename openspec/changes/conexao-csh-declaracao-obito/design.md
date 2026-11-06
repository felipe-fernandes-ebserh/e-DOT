# Design: Conexão CSH para Captura de Eventos de Declaração de Óbito

## Context & Motivation

No hospital, o registro de liberação de Declaração de Óbito é operacionalizado pela entrega física do material solicitado via Central de Serviços (CSH). O sistema CSH armazena essas solicitações na tabela `chamadomateriais`. Para a Triagem Obstétrica (`idLocal = 923`), as solicitações de material com `idTipoMaterial = 12` indicam a necessidade de declaração de óbito.

## Architecture & Layers

Seguindo estritamente a arquitetura do Framework SETISD HC-UFPE:
$$\text{SQL Template} \longrightarrow \text{Resource / Helper} \longrightarrow \text{Provider} \longrightarrow \text{Controller / Router}$$

### 1. Tratamento da URL CSH (`src/config.py` e helper de conexão)
A URL informada em `.env` possui formato:
`mysql://edot:edot123#@10.34.0.113:3306/centraldeservicos`
Devido ao caractere `#` na senha, o parser nativo do SQLAlchemy interpreta `#` como âncora/fragmento de URL e falha.
- **Solução**: Implementar normalização de URL no carregamento ou no provider que detecta o esquema `mysql://`, faz o encoding seguro da senha (`quote_plus`) e utiliza o driver assíncrono `mysql+asyncmy://` (ou `mysql+pymysql://` para fallback).

### 2. SQL Template (`src/providers/sql/csh/obitos_pendentes.sql`)
```sql
SELECT 
    cm.idChamadoMaterial AS id_evento_origem,
    cm.idChamadoMaterial AS id_chamado_material,
    COALESCE(NULLIF(TRIM(cm.pacienteChamado), ''), 'Identificação Pendente / Triagem Obstétrica') AS paciente_nome,
    NULL AS paciente_prontuario,
    NULL AS paciente_idade,
    'Triagem Obstétrica' AS leito,
    'Triagem Obstétrica' AS setor_obito,
    cm.dataCriacao AS data_hora_obito,
    cm.obs AS causa_obito,
    cm.solicitante AS medico_responsavel,
    cm.ramal AS ramal_contato,
    dcm.idLocal AS id_local_destino,
    cm.idTipoMaterial AS id_tipo_material
FROM chamadomateriais cm
INNER JOIN destinochamadomaterial dcm ON dcm.idChamadoMaterial = cm.idChamadoMaterial
WHERE cm.idTipoMaterial = 12
  AND dcm.idLocal = 923
  AND cm.isAtivo = 1
  AND cm.dataCancelamento IS NULL
ORDER BY cm.idChamadoMaterial DESC
LIMIT #limite;
```

### 3. Provider (`ObitoMySqlProvider`)
- Normaliza a string de conexão para `mysql+asyncmy://`.
- Executa a query assíncrona usando `create_async_engine` e mapeia para a lista de dicionários padrão esperada pelo controller de notificações.
- Permite parametrizar filtros (ex: limite de registros).

### 4. Controller & Router
- Controller verifica no banco local `data/app.db` (`NotificacaoObito`) se `id_evento_origem = str(row['id_evento_origem'])` já foi notificado.
- Se novo:
  - Formata o alerta (Modo Ocorrência Simples ou Completo com solicitante, ramal e horário de abertura do chamado).
  - Envia Adaptive Card com @menções individuais da equipe no Teams.
  - Grava na tabela `notificacoes_obitos` com `status = SUCESSO`.
- Endpoint `GET /api/notificacoes-obito/csh/teste-conexao` para validação em tela/painel administrativo.

## Security & Compliance
- Conexão em rede interna segura (VLAN do HC-UFPE).
- Credenciais lidas exclusivamente de variáveis de ambiente (`.env`).
- Conformidade de 100% no `audit_framework.py` mantida.

