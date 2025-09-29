from fastapi import APIRouter, status, Depends
from typing import Optional

from app.schemas.campanha import *
from app.services import campanha as campanha_service
from app.services.auth import get_current_user

router = APIRouter(prefix="/campanha", tags=["Campanha"])


@router.post("", response_model=CampanhaResponse, status_code=status.HTTP_201_CREATED)
def criar_campanha(payload: CreateCampanha, current_user: dict = Depends(get_current_user)):
    return campanha_service.criar_campanha(payload, current_user["id"])


@router.get("", response_model=List[CampanhaResponse])
def listar_campanhas(current_user: dict = Depends(get_current_user)):
    return campanha_service.listar_campanhas(current_user["id"], status)


@router.get("/{campanha_id}", response_model=CampanhaResponse)
def buscar_campanha(campanha_id: str, current_user: dict = Depends(get_current_user)):
    return campanha_service.buscar_campanha_por_id(campanha_id, current_user["id"])


@router.post("/{campanha_id}/acao", response_model=CampanhaResponse)
def enviar_acao(campanha_id: str, payload: AcaoJogador, current_user: dict = Depends(get_current_user)):
    """
    Envia uma ação do jogador na campanha
    A campanha processa a ação e retorna a resposta atualizada
    Atualmente retorna resposta mock. Integração com LLM será implementada em breve
    """
    return campanha_service.processar_acao_campanha(campanha_id, payload, current_user["id"])

@router.delete("/{campanha_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_campanha(campanha_id: str, current_user: dict = Depends(get_current_user)):

    campanha_service.deletar_campanha(campanha_id, current_user["id"])
    return None