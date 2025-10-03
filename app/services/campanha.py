import logging
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status

from app.db.database import campanhas_list, personagens_list
from app.schemas.campanha import *
from app.services.personagem import buscar_personagem_por_id
from app.services.llm import gerar_resposta_llm
from app.roteiro import ROTEIRO_DA_AVENTURA

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def _calcular_level_up(nivel_atual: int, xp_atual: int):
    # Verifica se o jogador subiu de nível com base em uma tabela fixa de XP
    limites_xp = {1: 100, 2: 250, 3: 500, 4: 1000}
    novo_nivel = nivel_atual
    xp_necessario = limites_xp.get(nivel_atual)
    if xp_necessario and xp_atual >= xp_necessario:
        novo_nivel += 1
        logger.info(f"LEVEL UP! Personagem atingiu o nível {novo_nivel}")
    return novo_nivel, xp_atual


def aplicar_regras_evento(evento: EventoInfo, estado_atual: dict, personagem: dict):
    # Aplica as regras do jogo ao estado do jogador com base no evento sugerido pelo LLM.
    novo_estado = estado_atual.copy()
    if evento.dano_sofrido > 0:
        novo_estado["vida_atual"] -= evento.dano_sofrido
        if novo_estado["vida_atual"] < 0:
            novo_estado["vida_atual"] = 0
    if evento.xp_ganho > 0:
        novo_estado["experiencia"] += evento.xp_ganho
    novo_nivel, _ = _calcular_level_up(novo_estado["nivel"], novo_estado["experiencia"])
    if novo_nivel > novo_estado["nivel"]:
        niveis_ganhos = novo_nivel - novo_estado["nivel"]
        constituicao = personagem["atributos"]["constituicao"]
        modificador_constituicao = (constituicao - 10) // 2
        bonus_vida_por_nivel = 5 + modificador_constituicao
        novo_estado["vida_maxima"] += bonus_vida_por_nivel * niveis_ganhos
        novo_estado["vida_atual"] += 10 * niveis_ganhos
        novo_estado["nivel"] = novo_nivel
    if evento.item_encontrado:
        if len(novo_estado.get("inventario", [])) < 10:
            novo_estado["inventario"].append(evento.item_encontrado)
        else:
            logger.warning(f"Inventário cheio. Item '{evento.item_encontrado}' foi descartado.")
    if novo_estado["vida_atual"] > novo_estado["vida_maxima"]:
        novo_estado["vida_atual"] = novo_estado["vida_maxima"]
    return novo_estado

def criar_campanha(dados: CreateCampanha, user_id: str):
    # Cria uma nova campanha para um personagem
    personagem = buscar_personagem_por_id(dados.personagem_id, user_id)
    estado_inicial = personagem.status.model_dump()

    resposta_llm_inicial = RespostaLLM(
        narrativa="Bem-vindo a Porto Sereno! A cidade está agitada hoje. Perto do cais, a taverna 'O Javali Risonho' parece um bom lugar para começar a procurar informações ou uma aventura.",
        acoesDisponiveis=["Ir para a taverna 'O Javali Risonho'", "Explorar o mercado",
                          "Falar com um guarda que está patrulhando"],
        evento=EventoInfo(tipo="inicio", chave_progresso=None),
        proximaEtapa="Encontre informações na cidade para começar sua jornada."
    )
    primeira_interacao = InteracaoHistorico(
        acao_jogador="[INÍCIO DA CAMPANHA]",
        resposta_llm=resposta_llm_inicial,
        timestamp=datetime.now()
    )

    campanha_doc = {
        "personagem_id": ObjectId(dados.personagem_id),
        "usuario_id": ObjectId(user_id),
        "status": StatusCampanha.ATIVA.value,
        "estado_atual": estado_inicial,
        "historico": [primeira_interacao.model_dump()],
        "criada_em": datetime.now(),
        "atualizada_em": datetime.now(),
        "etapa_historia": "inicio"
    }

    result = campanhas_list.insert_one(campanha_doc)
    campanha_doc["_id"] = result.inserted_id
    return campanha_db_to_response(campanha_doc)


async def processar_acao_campanha(campanha_id: str, acao: AcaoJogador, user_id: str):
    # Processa uma ação do jogador, orquestrando o roteiro, o LLM e as regras do jogo
    campanha_doc = campanhas_list.find_one({"_id": ObjectId(campanha_id), "usuario_id": ObjectId(user_id)})
    if not campanha_doc:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    if campanha_doc["status"] != StatusCampanha.ATIVA.value:
        raise HTTPException(status_code=400, detail="A campanha não está ativa.")

    personagem_pydantic = buscar_personagem_por_id(str(campanha_doc["personagem_id"]), user_id)
    personagem_doc = personagem_pydantic.model_dump()

    etapa_atual_id = campanha_doc.get("etapa_historia", "inicio")
    roteiro_etapa = ROTEIRO_DA_AVENTURA.get(etapa_atual_id)
    if not roteiro_etapa:
        logger.error(f"Etapa da história inválida '{etapa_atual_id}' na campanha {campanha_id}")
        raise HTTPException(status_code=500, detail="Erro interno: Etapa da história inválida.")

    resposta_llm_dict = await gerar_resposta_llm(
        personagem=personagem_doc,
        acao_jogador=acao.acao,
        historico=campanha_doc.get("historico", []),
        estado_atual=campanha_doc["estado_atual"],
        instrucoes_etapa=roteiro_etapa['instrucoes_narrador'],
        objetivo_etapa=roteiro_etapa['objetivo']
    )

    try:
        resposta_llm_validada = RespostaLLM(**resposta_llm_dict)
    except Exception as e:
        logger.error(f"LLM retornou JSON inválido: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar resposta da IA.")

    novo_estado_validado = aplicar_regras_evento(
        evento=resposta_llm_validada.evento,
        estado_atual=campanha_doc["estado_atual"],
        personagem=personagem_doc
    )

    nova_etapa_id = etapa_atual_id
    chave_recebida = resposta_llm_validada.evento.chave_progresso
    chave_esperada = roteiro_etapa.get("chave_para_avancar")

    if chave_recebida and chave_recebida == chave_esperada:
        proxima_etapa = roteiro_etapa.get("proxima_etapa")
        if proxima_etapa:
            nova_etapa_id = proxima_etapa
            logger.info(f"PROGRESSO DA HISTÓRIA! Campanha '{campanha_id}' avançou para: {nova_etapa_id}")
        else:
            logger.info(f"AVENTURA CONCLUÍDA! Campanha '{campanha_id}' chegou ao fim.")

    novo_status_campanha = campanha_doc["status"]
    if novo_estado_validado["vida_atual"] <= 0:
        novo_status_campanha = StatusCampanha.CONCLUIDA.value
        resposta_llm_validada.narrativa += "\n\nSua jornada chegou a um fim trágico."
        resposta_llm_validada.proximaEtapa = "O personagem morreu."
        resposta_llm_validada.acoesDisponiveis = []

    nova_interacao = InteracaoHistorico(
        acao_jogador=acao.acao,
        resposta_llm=resposta_llm_validada,
        timestamp=datetime.now()
    )

    campanhas_list.update_one(
        {"_id": ObjectId(campanha_id)},
        {
            "$push": {"historico": nova_interacao.model_dump()},
            "$set": {
                "atualizada_em": datetime.now(),
                "estado_atual": novo_estado_validado,
                "status": novo_status_campanha,
                "etapa_historia": nova_etapa_id
            }
        }
    )

    personagens_list.update_one(
        {"_id": ObjectId(personagem_doc["id"])},
        {"$set": {"status": novo_estado_validado}}
    )

    return buscar_campanha_por_id(campanha_id, user_id)


def listar_campanhas(user_id: str):
    busca = campanhas_list.find({"usuario_id": ObjectId(user_id)}).sort("atualizada_em", -1)
    return [campanha_db_to_response(c) for c in busca]


def buscar_campanha_por_id(campanha_id: str, user_id: str):
    try:
        oid = ObjectId(campanha_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de campanha inválido")

    campanha = campanhas_list.find_one({"_id": oid, "usuario_id": ObjectId(user_id)})
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")

    return campanha_db_to_response(campanha)


def deletar_campanha(campanha_id: str, user_id: str):
    try:
        oid = ObjectId(campanha_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de campanha inválido")

    result = campanhas_list.delete_one({"_id": oid, "usuario_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Campanha não encontrada para exclusão")

    return None


def campanha_db_to_response(campanha: dict) -> CampanhaResponse:
    # Converte um documento de campanha do MongoDB para o modelo de resposta Pydantic
    return CampanhaResponse(
        id=str(campanha["_id"]),
        personagem_id=str(campanha["personagem_id"]),
        usuario_id=str(campanha["usuario_id"]),
        status=StatusCampanha(campanha["status"]),
        historico=[InteracaoHistorico(**i) for i in campanha.get("historico", [])],
        estado_atual=campanha["estado_atual"],
        criada_em=campanha["criada_em"],
        atualizada_em=campanha["atualizada_em"],
        etapa_historia=campanha.get("etapa_historia", "inicio")
    )