from bson import ObjectId
from fastapi import HTTPException, status
from typing import List, Optional

from app.db.database import campanhas_list, personagens_list
from app.schemas.campanha import *
from app.services.personagem import buscar_personagem_por_id


def criar_campanha(dados: CreateCampanha, user_id: str):

    # Valida se personagem existe e pertence ao usuário
    personagem = buscar_personagem_por_id(dados.personagem_id, user_id)

    # TODO: Integrar LLM aqui
    narrativa_inicial = (
        f"Bem-vindo, {personagem.nome}! "
        f"Sua aventura como {personagem.classe} {personagem.raca} está prestes a começar. "
        f"O que você deseja fazer?"
    )

    # Estado inicial da campanha
    estado_inicial = {
        "vida_atual": personagem.status.vida_atual,
        "vida_maxima": personagem.status.vida_maxima,
        "nivel": personagem.status.nivel,
        "experiencia": personagem.status.experiencia,
        "inventario": personagem.status.inventario.copy()
    }

    # Primeira interação (introdução)
    primeira_interacao = {
        "acao_jogador": "[INÍCIO DA CAMPANHA]",
        "resposta_llm": {
            "narrativa": narrativa_inicial,
            "acoesDisponiveis": ["Explorar", "Descansar", "Procurar por aventuras"],
            "evento": {"tipo": "inicio"},
            "estadoJogador": estado_inicial,
            "proximaEtapa": "Escolha uma ação para começar sua jornada."
        },
        "timestamp": datetime.now()
    }

    # Documento da campanha
    campanha = {
        "personagem_id": ObjectId(dados.personagem_id),
        "usuario_id": ObjectId(user_id),
        "status": StatusCampanha.ATIVA.value,
        "estado_atual": estado_inicial,
        "historico": [primeira_interacao],
        "criada_em": datetime.now(),
        "atualizada_em": datetime.now()
    }

    # Insere no banco
    result = campanhas_list.insert_one(campanha)

    # Retorna a campanha criada
    campanha["_id"] = result.inserted_id
    return campanha_db(campanha)

def listar_campanhas(user_id: str):
    busca = campanhas_list.find({"usuario_id": ObjectId(user_id)}).sort("atualizada_em", -1)
    return [campanha_db(campanha) for campanha in busca]

# Buscar campanha por ID e valida se é dono da campanha
def buscar_campanha_por_id(campanha_id: str, user_id: str):
    try:
        oid = ObjectId(campanha_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de campanha inválido"
        )

    campanha = campanhas_list.find_one({
        "_id": oid,
        "usuario_id": ObjectId(user_id)
    })

    if not campanha:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada"
        )

    return campanha_db(campanha)


def processar_acao_campanha(campanha_id: str, acao: AcaoJogador, user_id: str):
    # Busca campanha
    campanha = buscar_campanha_por_id(campanha_id, user_id)

    # Valida se campanha está ativa
    if campanha.status != StatusCampanha.ATIVA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Campanha está {campanha.status.value}. Apenas campanhas ativas podem receber ações."
        )

    # TODO: Integrar LLM aqui
    # Por enquanto, resposta mock simples
    resposta_teste = {
        "narrativa": f"Você tentou: '{acao.acao}'. Esta é uma resposta temporária.",
        "acoesDisponiveis": ["Continuar", "Explorar", "Descansar"],
        "evento": {
            "tipo": "acao_temporaria",
            "acao_realizada": acao.acao
        },
        "estadoJogador": campanha.estado_atual,  # Mantém estado atual
        "continue": "Continua a aventura."
    }

    nova_interacao = {
        "acao_jogador": acao.acao,
        "resposta_llm": resposta_teste,
        "timestamp": datetime.now()
    }

    # Atualiza campanha no banco
    campanhas_list.update_one(
        {"_id": ObjectId(campanha_id)},
        {
            "$push": {"historico": nova_interacao},
            "$set": {
                "atualizada_em": datetime.now(),
                # TODO: Atualizar estado_atual baseado na resposta da LLM
            }
        }
    )

    # Retorna campanha atualizada
    return buscar_campanha_por_id(campanha_id, user_id)


def encerrar_campanha(campanha_id: str, user_id: str):
    # Busca campanha e verifica se é dono
    campanha = buscar_campanha_por_id(campanha_id, user_id)

    # Atualiza status
    campanhas_list.update_one(
        {"_id": ObjectId(campanha_id)},
        {
            "$set": {
                "status": StatusCampanha.CONCLUIDA.value,
                "atualizada_em": datetime.now()
            }
        }
    )

    return buscar_campanha_por_id(campanha_id, user_id)

def deletar_campanha(campanha_id: str, user_id: str):
    try:
        oid = ObjectId(campanha_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de campanha inválido"
        )

    result = campanhas_list.delete_one({
        "_id": oid,
        "usuario_id": ObjectId(user_id)
    })

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada"
        )

    return True


def campanha_db(campanha: dict) -> CampanhaResponse:
    # Converte histórico
    historico = []
    for interacao in campanha.get("historico", []):
        historico.append(InteracaoHistorico(
            acao_jogador=interacao["acao_jogador"],
            resposta_llm=interacao["resposta_llm"],
            timestamp=interacao["timestamp"]
        ))

    return CampanhaResponse(
        id=str(campanha["_id"]),
        personagem_id=str(campanha["personagem_id"]),
        usuario_id=str(campanha["usuario_id"]),
        status=StatusCampanha(campanha["status"]),
        historico=historico,
        estado_atual=campanha["estado_atual"],
        criada_em=campanha["criada_em"],
        atualizada_em=campanha["atualizada_em"]
    )