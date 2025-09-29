from bson import ObjectId
from fastapi import HTTPException, status
from datetime import datetime

from app.db.database import personagens_list
from app.schemas.personagem import CreatePersonagem, Personagem, StatusJogo


def calcular_vida_maxima(constituicao: int):
    return 10 + (constituicao * 2) # Cada ponto em constituição é equivalente ao dobro do valor em hp


def criar_personagem(dados: CreatePersonagem, user_id: str):

    vida_max = calcular_vida_maxima(dados.atributos.constituicao)
    personagem = {
        "nome": dados.nome,
        "raca": dados.raca.value,
        "classe": dados.classe.value,
        "descricao": dados.descricao,
        "atributos": dados.atributos.model_dump(),
        "status": {
            "nivel": 1,
            "vida_maxima": vida_max,
            "vida_atual": vida_max,
            "experiencia": 0,
            "inventario": []
        },
        "usuario_id": ObjectId(user_id),
        "criado_em": datetime.now()
    }

    result = personagens_list.insert_one(personagem)

    # Retorna o personagem criado
    personagem["_id"] = result.inserted_id
    return personagem_db(personagem)


def listar_personagens(user_id: str):

    busca = personagens_list.find({"usuario_id": ObjectId(user_id)})
    return [personagem_db(personagem) for personagem in busca]


def buscar_personagem_por_id(personagem_id: str, user_id: str):
    # Buscar por id e verificar se é dono do personagem
    try:
        oid = ObjectId(personagem_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de personagem inválido"
        )

    personagem = personagens_list.find_one({
        "_id": oid,
        "usuario_id": ObjectId(user_id)
    })

    if not personagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personagem não encontrado"
        )

    return personagem_db(personagem)


def deletar_personagem(personagem_id: str, user_id: str):

    try:
        oid = ObjectId(personagem_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de personagem inválido"
        )

    personagens_list.delete_one({
        "_id": oid,
        "usuario_id": ObjectId(user_id)
    })
    return True


def personagem_db(personagem: dict) -> Personagem:
    # Converte documento do Banco para Pydantic

    return Personagem(
        id=str(personagem["_id"]),
        nome=personagem["nome"],
        raca=personagem["raca"],
        classe=personagem["classe"],
        descricao=personagem["descricao"],
        atributos=personagem["atributos"],
        status=StatusJogo(**personagem["status"]),
        usuario_id=str(personagem["usuario_id"]),
        criado_em=personagem["criado_em"]
    )