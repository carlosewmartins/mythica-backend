# Mythica RPG - Backend

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)

Este é o backend da aplicação Mythica RPG, uma API RESTful desenvolvida com FastAPI para gerenciar a lógica de um jogo de RPG interativo. A API é responsável pela autenticação de usuários, criação e gerenciamento de personagens e campanhas, e pela integração com um modelo de linguagem (LLM) da OpenAI para gerar narrativas dinâmicas.

---

## ✨ Funcionalidades Principais

* **Autenticação JWT**: Sistema seguro de `signup` e `login` com tokens JWT.
* **Gerenciamento de Personagens**: CRUD completo para os personagens dos jogadores.
* **Gerenciamento de Campanhas**: Criação, listagem e exclusão de campanhas.
* **Gameplay Interativo**: Processa as ações dos jogadores e utiliza um LLM (OpenAI) para gerar as respostas e o desenrolar da história.
* **Lógica de Jogo**: Aplica regras de dano, ganho de XP, level up e gerenciamento de inventário.

---

## 🛠️ Tecnologias Utilizadas

* **Framework**: FastAPI
* **Linguagem**: Python
* **Banco de Dados**: MongoDB (com Pymongo)
* **Autenticação**: Passlib, PyJWT
* **Validação de Dados**: Pydantic
* **Servidor**: Uvicorn
* **Inteligência Artificial**: OpenAI API

---

## 🚀 Rodando Localmente

Siga os passos abaixo para configurar e rodar o projeto em seu ambiente local.

### Pré-requisitos

* Python 3.8 ou superior
* MongoDB instalado e rodando localmente (ou uma instância na nuvem)
* Uma chave de API da OpenAI

### Passos

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/carlosewmartins/mythica-backend
    cd mythica-backend
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Windows
    python -m venv .venv
    .\.venv\Scripts\activate

    # Linux / macOS
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    * Renomeie o arquivo `.env.example` para `.env`.
    * Abra o arquivo `.env` e preencha as variáveis necessárias:
        ```env
        # ===== CONFIG =====
        PROJECT_NAME="Mythica RPG API - Local"
        VERSION="1.0.0"

        # ===== SECURITY =====
        SECRET_KEY="gere-uma-chave-secreta-forte"
        JWT_EXPIRATION_MINUTES=1440
        ALGORITHM="HS256"

        # ===== DATABASE (Local) =====
        MONGODB_URL="mongodb://localhost:27017"
        DATABASE_NAME="mythica_dev"

        # ===== CORS =====
        CORS="http://localhost:4200"

        # ===== LLM (OpenAI) =====
        OPENAI_API_KEY="sua-chave-da-openai-aqui"
        OPENAI_BASE_URL="[https://api.openai.com/v1](https://api.openai.com/v1)"
        OPENAI_MODEL="gpt-4o-mini"
        LLM_MAX_TOKENS=2000
        LLM_TEMPERATURE=0.7
        ```

5.  **Execute a aplicação:**
    ```bash
    uvicorn app.main:app --reload
    ```
    A API estará disponível em `http://127.0.0.1:8000`.

---

## ☁️ Versão em Produção (Deploy)

A API também está disponível online e pode ser acessada através da seguinte URL:

* **URL Base da API**: `https://mythica-backend.onrender.com`
* **Documentação Interativa (Swagger UI)**: `https://mythica-backend.onrender.com/docs`

O frontend em produção já está configurado para se comunicar com esta versão da API.
