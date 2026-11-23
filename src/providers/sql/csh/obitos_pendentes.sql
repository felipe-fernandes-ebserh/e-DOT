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
    COALESCE(l_orig.nomeLocal, 'Setor não identificado') AS setor_solicitante,
    'Triagem Obstétrica' AS setor_destino,
    cm.dataCriacao AS data_hora_obito,
    cm.obs AS causa_obito,
    cm.solicitante AS medico_responsavel,
    cm.ramal AS ramal_contato,
    cm.idOrigem AS id_local_origem,
    dcm.idLocal AS id_local_destino,
    cm.idTipoMaterial AS id_tipo_material
FROM chamadomateriais cm
INNER JOIN destinochamadomaterial dcm ON dcm.idChamadoMaterial = cm.idChamadoMaterial
LEFT JOIN local l_orig ON l_orig.idLocal = cm.idOrigem
WHERE cm.idTipoMaterial = #id_tipo_material
  AND dcm.idLocal = #id_local_destino
  AND cm.isAtivo = 1
  AND cm.dataCancelamento IS NULL
ORDER BY cm.idChamadoMaterial DESC
LIMIT #limite;
