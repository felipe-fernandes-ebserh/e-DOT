"""
Helper de Formatação de Cartões Adaptativos para o Microsoft Teams (Adaptive Cards v1.2+)
========================================================================================
Monta payloads estruturados para envio via Webhook do Microsoft Teams contendo @menções
individuais (msteams.entities) e suporte a Modo Completo (dados clínicos) e Modo Alerta Simples.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


def build_teams_adaptive_card(dados_obito: Dict[str, Any], destinatarios: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """
    Constrói o payload JSON do Adaptive Card formatado para o canal do Teams.
    
    :param dados_obito: Dicionário contendo os dados do óbito (nome_paciente, idade, setor_leito, causa_morte, prontuario, data_hora_obito, etc).
    :param destinatarios: Lista de destinatários com 'nome' e 'email_teams'.
    :return: Dicionário serializável em JSON pronto para envio HTTP ao Webhook.
    """
    destinatarios = destinatarios or []
    
    # 1. Montagem das menções individuais (@mentions) desduplicadas
    mention_tags: List[str] = []
    mention_entities: List[Dict[str, Any]] = []
    seen_emails = set()
    
    for d in destinatarios:
        nome = d.get("nome", "").strip()
        email = d.get("email_teams", "").strip().lower()
        if nome and email and email not in seen_emails:
            seen_emails.add(email)
            tag = f"<at>{nome}</at>"
            mention_tags.append(tag)
            mention_entities.append({
                "type": "mention",
                "text": tag,
                "mentioned": {
                    "id": email,
                    "name": nome
                }
            })
    
    mention_text = "Atenção: " + ", ".join(mention_tags) if mention_tags else "Notificação Geral da Busca Ativa (CIHDOTT)"
    
    # 2. Identificação do Modo de Apresentação
    nome_paciente = dados_obito.get("nome_paciente")
    is_completo = bool(nome_paciente and str(nome_paciente).strip())
    
    # Formatação de data/hora
    data_hora = dados_obito.get("data_hora_obito")
    if isinstance(data_hora, datetime):
        data_hora_str = data_hora.strftime("%d/%m/%Y %H:%M")
    elif data_hora:
        data_hora_str = str(data_hora)
    else:
        data_hora_str = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M (UTC)")
        
    setor_leito = dados_obito.get("setor_leito") or "Setor/Leito não informado"
    
    card_body: List[Dict[str, Any]] = []
    
    if is_completo:
        # --- MODO COMPLETO: DADOS CLÍNICOS DISPONÍVEIS ---
        card_body.append({
            "type": "TextBlock",
            "size": "Medium",
            "weight": "Bolder",
            "color": "Attention",
            "text": "🚨 ALERTA DE ÓBITO — BUSCA ATIVA"
        })
        card_body.append({
            "type": "TextBlock",
            "text": mention_text,
            "wrap": True,
            "weight": "Bolder" if mention_tags else "Default"
        })
        
        prontuario = dados_obito.get("prontuario")
        prontuario_str = str(prontuario) if prontuario and str(prontuario).strip() else "⚠️ PENDENTE / EM VERIFICAÇÃO"
        
        idade = dados_obito.get("idade")
        idade_str = f"{idade} anos" if idade is not None else "Não informada"
        
        causa = dados_obito.get("causa_morte") or "Não informada / A apurar"
        
        facts = [
            {"title": "Paciente:", "value": str(nome_paciente)},
            {"title": "Idade:", "value": idade_str},
            {"title": "Localização:", "value": str(setor_leito)},
            {"title": "Causa da Morte:", "value": str(causa)},
            {"title": "Prontuário:", "value": prontuario_str},
            {"title": "Data/Hora:", "value": data_hora_str}
        ]
        
        card_body.append({
            "type": "FactSet",
            "facts": facts
        })
    else:
        # --- MODO ALERTA SIMPLES: APENAS OCORRÊNCIA CONFIRMADA ---
        card_body.append({
            "type": "TextBlock",
            "size": "Medium",
            "weight": "Bolder",
            "color": "Attention",
            "text": "🚨 ALERTA DE ÓBITO HOSPITALAR"
        })
        card_body.append({
            "type": "TextBlock",
            "text": mention_text,
            "wrap": True,
            "weight": "Bolder" if mention_tags else "Default"
        })
        
        facts = [
            {"title": "Ocorrência:", "value": "Óbito hospitalar confirmado no sistema"},
            {"title": "Localização:", "value": str(setor_leito)},
            {"title": "Data/Hora:", "value": data_hora_str},
            {"title": "Identificação:", "value": "Dados do paciente pendentes de cadastro na origem"}
        ]
        
        card_body.append({
            "type": "FactSet",
            "facts": facts
        })
        card_body.append({
            "type": "TextBlock",
            "text": "ℹ️ Orientação: Iniciar busca ativa presencial imediatamente na unidade indicada para acolhimento da família e checagem do prontuário.",
            "wrap": True,
            "isSubtle": True,
            "color": "Warning"
        })

    adaptive_card = {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.2",
        "type": "AdaptiveCard",
        "body": card_body
    }
    
    if mention_entities:
        adaptive_card["msteams"] = {
            "entities": mention_entities
        }
        
    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": adaptive_card
            }
        ]
    }
    
    return payload
