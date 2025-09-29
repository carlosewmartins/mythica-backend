from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Dict, Any, List

class StatusCampanha(str, Enum):
    ATIVA = "ativa"
    PAUSADA = "pausada"
    CONCLUIDA = "concluida"


class InteracaoHistorico(BaseModel):
    acao_jogador: str
    resposta_llm: Dict[str, Any]
    timestamp: datetime


class CreateCampanha(BaseModel):
    personagem_id: str


class AcaoJogador(BaseModel):
    acao: str = Field(..., min_length=1, max_length=200)


class CampanhaResponse(BaseModel):
    id: str
    personagem_id: str
    usuario_id: str
    status: StatusCampanha
    historico: List[InteracaoHistorico]
    estado_atual: Dict[str, Any]
    criada_em: datetime
    atualizada_em: datetime