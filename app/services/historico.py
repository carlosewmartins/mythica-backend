from bson import ObjectId
from fastapi import HTTPException, status
from datetime import datetime

from app.db.database import campanhas_list
from app.services.campanha import buscar_campanha_por_id


def buscar_historico(campanha_id: str, user_id: str):
    # Retorna histórico e verifica se é dono da campanha
    campanha = buscar_campanha_por_id(campanha_id, user_id)
    return campanha.historico


def limpar_historico(campanha_id: str, user_id: str) -> dict:
    # Verifica se é dono da campanha antes de limpar histórico
    campanha = buscar_campanha_por_id(campanha_id, user_id)

    # Valida que campanha tem histórico
    if not campanha.historico:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campanha não possui histórico para limpar"
        )

    # Preserva apenas a introdução
    primeira_interacao = campanha.historico[0]

    # Reseta o estado do jogador para o inicial (pega do estado da primeira interação)
    estado_inicial = primeira_interacao.resposta_llm.get("estadoJogador", campanha.estado_atual)

    # Atualiza no banco
    campanhas_list.update_one(
        {"_id": ObjectId(campanha_id)},
        {
            "$set": {
                "historico": [{
                    "acao_jogador": primeira_interacao.acao_jogador,
                    "resposta_llm": primeira_interacao.resposta_llm,
                    "timestamp": primeira_interacao.timestamp
                }],
                "estado_atual": estado_inicial,
                "atualizada_em": datetime.now()
            }
        }
    )

    return {"mensagem": "Histórico limpo com sucesso. A campanha foi resetada para o início."}