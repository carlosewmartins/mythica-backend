from fastapi import APIRouter, status, Depends
from typing import List

from app.schemas.campanha import InteracaoHistorico
from app.services import historico as historico_service
from app.services.auth import get_current_user

router = APIRouter(prefix="/historico", tags=["Histórico"])


@router.get("/{campanha_id}", response_model=List[InteracaoHistorico])
def buscar_historico(campanha_id: str, current_user: dict = Depends(get_current_user)):
    return historico_service.buscar_historico(campanha_id, current_user["id"])


@router.delete("/{campanha_id}", status_code=status.HTTP_200_OK)
def limpar_historico(campanha_id: str, current_user: dict = Depends(get_current_user)):
    return historico_service.limpar_historico(campanha_id, current_user["id"])