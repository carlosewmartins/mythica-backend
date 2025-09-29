from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from app.schemas.personagem import CreatePersonagem, Personagem
from app.services import personagem as personagem_service
from app.services.auth import get_current_user, oauth2_scheme

router = APIRouter(prefix="/personagem", tags=["Personagem"])


@router.post("", response_model=Personagem, status_code=status.HTTP_201_CREATED)
def criar_personagem(
        payload: CreatePersonagem,
        current_user: dict = Depends(get_current_user)):

    return personagem_service.criar_personagem(payload, current_user["id"])


@router.get("", response_model=List[Personagem])
def listar_personagens(
        current_user: dict = Depends(get_current_user)):

    return personagem_service.listar_personagens(current_user["id"])


@router.get("/{personagem_id}", response_model=Personagem)
def buscar_personagem(
        personagem_id: str,
        current_user: dict = Depends(get_current_user)):

    return personagem_service.buscar_personagem_por_id(personagem_id, current_user["id"])


@router.delete("/{personagem_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_personagem(
        personagem_id: str,
        current_user: dict = Depends(get_current_user)):
    personagem_service.deletar_personagem(personagem_id, current_user["id"])
    return None