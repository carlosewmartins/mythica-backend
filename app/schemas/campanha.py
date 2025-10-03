from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Dict, Any, List, Optional

class StatusCampanha(str, Enum):
    ATIVA = "ativa"
    PAUSADA = "pausada"
    CONCLUIDA = "concluida"

class EventoInfo(BaseModel):
    tipo: str = Field(..., description="Tipo do evento: combate, exploracao, dialogo, etc.")
    dano_sofrido: int = Field(0, description="Dano que o jogador sofreu neste turno.")
    xp_ganho: int = Field(0, description="XP que o jogador ganhou.")
    inimigo_derrotado: bool = Field(False, description="Se um inimigo foi derrotado.")
    item_encontrado: Optional[str] = Field(None, description="Nome do item encontrado, se houver.")
    chave_progresso: Optional[str] = Field(None, description="Chave secreta que sinaliza o avanço da história.")

class RespostaLLM(BaseModel):
    narrativa: str
    acoesDisponiveis: List[str]
    evento: EventoInfo
    proximaEtapa: Optional[str] = None

class InteracaoHistorico(BaseModel):
    acao_jogador: str
    resposta_llm: RespostaLLM
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
    etapa_historia: str