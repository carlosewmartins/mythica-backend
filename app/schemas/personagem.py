from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class RacaEnum(str, Enum):
    HUMANO = "Humano"
    ELFO = "Elfo"
    ANAO = "Anão"
    ORC = "Orc"

class ClasseEnum(str, Enum):
    GUERREIRO = "Guerreiro"
    MAGO = "Mago"
    LADINO = "Ladino"
    CLERIGO = "Clérigo"
    ARQUEIRO = "Arqueiro"

class AtributosBase(BaseModel):
    forca: int = Field(..., ge=1, le=20, description="Força (1-20)")
    destreza: int = Field(..., ge=1, le=20, description="Destreza (1-20)")
    constituicao: int = Field(..., ge=1, le=20, description="Constituição (1-20)")
    inteligencia: int = Field(..., ge=1, le=20, description="Inteligência (1-20)")
    sabedoria: int = Field(..., ge=1, le=20, description="Sabedoria (1-20)")
    carisma: int = Field(..., ge=1, le=20, description="Carisma (1-20)")
    PONTOS_INICIAIS: int = 27

    @model_validator(mode='after')
    def validar_distribuicao_pontos(self):
        total = (self.forca + self.destreza + self.constituicao +
                 self.inteligencia + self.sabedoria + self.carisma)

        if total > self.PONTOS_INICIAIS:
            raise ValueError(
                f'Total de pontos ({total}) excede limite de {self.PONTOS_INICIAIS}. '
                f'Redistribua os pontos.'
            )

        if total < self.PONTOS_INICIAIS :
            raise ValueError(
                f'Você precisa utilizar todos os {self.PONTOS_INICIAIS} pontos. Você só utilizou {total} pontos.'
            )

        return self

class StatusJogo(BaseModel):
    nivel: int = Field(default=1, ge=1)
    vida_maxima: int = Field(..., ge=10)
    vida_atual: int = Field(..., ge=0)
    experiencia: int = Field(default=0, ge=0)
    inventario: List[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def validar_vida(self):
        if self.vida_atual > self.vida_maxima:
            raise ValueError('Vida atual não pode ser maior que vida máxima')
        return self

class CreatePersonagem(BaseModel):
    nome: str = Field(..., min_length=2, max_length=50)
    raca: RacaEnum
    classe: ClasseEnum
    descricao: str = Field(..., max_length=500)
    atributos: AtributosBase

class Personagem(BaseModel):
    id: str
    nome: str
    raca: str
    classe: str
    descricao: str
    atributos: AtributosBase
    status: StatusJogo
    usuario_id: str
    criado_em: datetime