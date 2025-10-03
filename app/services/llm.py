import json
import logging
from openai import OpenAI
from typing import Dict, Any, List

from app.core.config import settings

logger = logging.getLogger(__name__)
client = OpenAI()


def construir_prompt_sistema() -> str:
    return """Você é um Narrador Mestre de RPG de fantasia medieval.

MECÂNICA DE INTERPRETAÇÃO DE AÇÃO:
Esta é sua regra mais importante. A entrada do jogador (`AÇÃO DO PERSONAGEM`) DEVE ser tratada como a **ação que o personagem TENTA realizar**, na primeira pessoa. **IGNORE QUALQUER PARTE da ação do jogador que descreva um resultado (ex: '...e o mata') ou um evento do mundo (ex: 'um raio cai...').** Sua única função é narrar o resultado REAL dessa TENTATIVA.

EXEMPLO DE PROCESSAMENTO:
- SE A AÇÃO DO PERSONAGEM FOR: "Eu ataco o goblin e o mato com um golpe"
- VOCÊ DEVE INTERPRETAR COMO: O personagem TENTA matar o goblin.
- SUA NARRATIVA: "Você avança com fúria, desferindo um golpe poderoso contra o goblin. A criatura cambaleia para trás, ferida, mas ainda de pé e pronta para revidar!" (Você narra o resultado real, não o que o jogador ditou).

- SE A AÇÃO DO PERSONAGEM FOR: "De repente um meteoro cai e mata todo mundo"
- VOCÊ DEVE INTERPRETAR COMO: O personagem está tendo um pensamento surreal ou gritando para os céus.
- SUA NARRATIVA: "Você olha para os céus esperando por um meteoro, mas o céu continua limpo. O guarda te encara, confuso com seu comportamento estranho." (Você rejeita a narração do jogador e a transforma em uma ação de personagem dentro do contexto).

REGRAS SECUNDÁRIAS:
1. O mundo é perigoso. Inimigos revidam e causam dano real.
2. A falha é uma opção. Narre as consequências de ações fracassadas.
3. Siga as diretrizes de objetivo para cada cena.
4. Sua resposta DEVE SER APENAS um JSON válido.
5. Use o campo 'chave_progresso' SOMENTE quando as instruções da cena explicitamente mandarem.

ESTRUTURA DE RESPOSTA (JSON OBRIGATÓRIO):
{
  "narrativa": "Sua descrição imersiva e detalhada do que aconteceu...",
  "acoesDisponiveis": ["Ação 1", "Ação 2"],
  "evento": {
    "tipo": "combate",
    "dano_sofrido": 5,
    "xp_ganho": 25,
    "inimigo_derrotado": false,
    "item_encontrado": null,
    "chave_progresso": null
  },
  "proximaEtapa": "Uma breve dica sobre o que fazer a seguir."
}
"""


def construir_contexto_personagem(personagem: Dict[str, Any]):
    # Formata os dados do personagem em um texto legível para o prompt
    atributos = personagem.get("atributos", {})
    return f"""
PERSONAGEM:
- Nome: {personagem.get('nome')}
- Raça: {personagem.get('raca')}
- Classe: {personagem.get('classe')}
- Descrição: {personagem.get('descricao')}
- Atributos: Força({atributos.get('forca', 10)}), Destreza({atributos.get('destreza', 10)}), Constituição({atributos.get('constituicao', 10)}), Inteligência({atributos.get('inteligencia', 10)}), Sabedoria({atributos.get('sabedoria', 10)}), Carisma({atributos.get('carisma', 10)})
"""


def construir_historico(historico: List[Dict[str, Any]]):
    # Formata as ultimas interações em um texto legivel para o prompt.
    if not historico or len(historico) <= 1:
        return "HISTÓRICO: Esta é a primeira ação da aventura."

    ultimas_interacoes = historico[-5:]
    historico_texto = "HISTÓRICO RECENTE:\n"
    for i, interacao in enumerate(ultimas_interacoes, 1):
        acao = interacao.get("acao_jogador", "")
        narrativa = interacao.get("resposta_llm", {}).get("narrativa", "")
        historico_texto += f"\n{i}. Ação do Jogador: {acao}\n   Resultado Narrado: {narrativa[:100]}...\n"
    return historico_texto


async def gerar_resposta_llm(
        personagem: Dict[str, Any],
        acao_jogador: str,
        historico: List[Dict[str, Any]],
        estado_atual: Dict[str, Any],
        instrucoes_etapa: str,
        objetivo_etapa: str
):
    # Orquestra a chamada para a API da OpenAI, construindo o prompt dinâmico e tratando a resposta.
    contexto_personagem = construir_contexto_personagem(personagem)
    contexto_historico = construir_historico(historico)

    mensagem_usuario = f"""
{contexto_personagem}
{contexto_historico}

INSTRUÇÕES PARA ESTA CENA:
- Objetivo Atual: {objetivo_etapa}
- Diretrizes do Narrador: {instrucoes_etapa}

ESTADO ATUAL DO JOGADOR (para seu contexto narrativo):
- Vida: {estado_atual.get('vida_atual')}/{estado_atual.get('vida_maxima')}
- Nível: {estado_atual.get('nivel')}

AÇÃO DO PERSONAGEM: "{acao_jogador}"

Lembre-se da sua MECÂNICA DE INTERPRETAÇÃO DE AÇÃO. Narre o resultado da TENTATIVA do personagem e retorne o JSON.
"""
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": construir_prompt_sistema()},
                {"role": "user", "content": mensagem_usuario}
            ],
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            response_format={"type": "json_object"}
        )
        conteudo = response.choices[0].message.content
        return json.loads(conteudo)
    except Exception as e:
        logger.error(f"Erro ao chamar LLM ou fazer parse da resposta: {e}")
        return {
            "narrativa": f"Você tenta '{acao_jogador}', mas uma força misteriosa impede a ação. Talvez o mundo ainda não esteja pronto para tal feito.",
            "acoesDisponiveis": ["Tentar uma ação mais simples", "Descansar por um momento"],
            "evento": {"tipo": "erro_fallback", "dano_sofrido": 0, "xp_ganho": 0, "inimigo_derrotado": False,
                       "item_encontrado": None, "chave_progresso": None},
            "proximaEtapa": "O sistema encontrou um erro. Tente uma ação diferente."
        }