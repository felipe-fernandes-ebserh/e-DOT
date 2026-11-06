-- ==============================================================================
-- Query: Obtenção de Solicitações de Declaração de Óbito no CSH (MySQL)
-- Busca solicitações na tabela chamadomateriais destinadas a setores monitorados
-- (ex: Triagem Obstétrica idLocal: 923) para material de Declaração de Óbito (idTipoMaterial: 12)
-- ==============================================================================
SELECT 
    CAST(cm.idChamadoMaterial AS CHAR) AS id_evento_origem,
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
WHERE cm.idTipoMaterial = #id_tipo_material
  AND dcm.idLocal = #id_local_destino
  AND cm.isAtivo = 1
  AND cm.dataCancelamento IS NULL
ORDER BY cm.idChamadoMaterial DESC
LIMIT #limite;
