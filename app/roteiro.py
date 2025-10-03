"""
Cada etapa define:
- objetivo: O que o jogador precisa fazer para avançar.
- instrucoes_narrador: Diretrizes para a IA sobre o tom, inimigos e eventos da etapa.
- proxima_etapa: O ID da etapa seguinte após a conclusão do objetivo.
- chave_para_avancar: Uma "senha" que a IA deve retornar para o backend autorizar a progressão.
"""

ROTEIRO_DA_AVENTURA = {
    "inicio": {
        "objetivo": "Falar com o taverneiro na 'Taverna do Javali Risonho' para descobrir sobre os desaparecimentos na floresta.",
        "instrucoes_narrador": (
            "A cena se passa na cidade de Porto Sereno. A atmosfera é segura. Evite combates, a menos que o jogador inicie uma agressão clara e não provocada. "
            "Se ele atacar um guarda, o guarda deve revidar e causar dano (dano_sofrido entre 2-5). "
            "Se o jogador falar com qualquer pessoa que não seja o taverneiro, forneça uma pista ou um boato, mas NÃO avance a história. "
            "SOMENTE QUANDO o jogador falar com o taverneiro e aceitar a missão sobre os desaparecimentos, você DEVE retornar 'chave_progresso': 'MISSÃO_ACEITA'."
        ),
        "proxima_etapa": "investigacao_floresta",
        "chave_para_avancar": "MISSÃO_ACEITA"
    },
    "investigacao_floresta": {
        "objetivo": "Encontrar 3 pistas na floresta: um acampamento abandonado, um símbolo de culto e pegadas de goblins.",
        "instrucoes_narrador": (
            "O jogador está na Floresta Sussurrante. O desafio é médio. Inimigos como lobos (fracos, 10 HP) podem aparecer e devem atacar primeiro se o jogador não for cauteloso. O combate deve ser um risco real (dano_sofrido entre 3-6). "
            "O jogador precisa encontrar 3 itens específicos ('Pista: Acampamento', 'Pista: Símbolo de Culto', 'Pista: Pegadas'). "
            "SOMENTE QUANDO o jogador tiver encontrado a TERCEIRA e última pista, você DEVE retornar 'chave_progresso': 'PISTAS_ENCONTRADAS'."
        ),
        "proxima_etapa": "covil_goblins",
        "chave_para_avancar": "PISTAS_ENCONTRADAS"
    },
    "covil_goblins": {
        "objetivo": "Derrotar o Chefe Goblin 'Grishnak' e recuperar o medalhão roubado.",
        "instrucoes_narrador": (
            "O desafio aqui é alto. O jogador está no covil dos goblins. Os goblins usam táticas, atacam em grupos de 2 a 3 e são agressivos (dano_sofrido entre 4-8 por turno de combate). "
            "O Chefe Goblin Grishnak (médio, 40 HP) é mais forte e pode causar até 10 de dano. "
            "SOMENTE QUANDO Grishnak for derrotado, você DEVE retornar 'chave_progresso': 'CHEFE_DERROTADO'."
        ),
        "proxima_etapa": "final",
        "chave_para_avancar": "CHEFE_DERROTADO"
    },
    "final": {
        "objetivo": "Retornar a Porto Sereno e receber a recompensa.",
        "instrucoes_narrador": "O perigo passou. Narre o retorno heróico do jogador a Porto Sereno e a recompensa recebida. Não há mais progressão de história.",
        "proxima_etapa": None,
        "chave_para_avancar": None
    }
}