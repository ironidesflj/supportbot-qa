# SupportBot QA 🤖

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![LangChain](https://img.shields.io/badge/LangChain-121212?style=for-the-badge)
![Qdrant](https://img.shields.io/badge/Qdrant-f90b49?style=for-the-badge)

Um sistema avançado de **Inteligência Artificial de Suporte (RAG)** focado em Qualidade (QA). O projeto permite que administradores façam upload de bases de conhecimento (PDFs ou Textos) e interajam com o conteúdo através de um Chatbot inteligente.

Caso a resposta para a dúvida do usuário não esteja nos documentos vetorizados, o sistema possui um **Agente Autônomo de Fallback** (*Function Calling*) que busca a resposta em tempo real na internet utilizando a API do Katzilla.

## 🌟 Principais Funcionalidades

- **Arquitetura Híbrida Multi-Model**: Suporte dinâmico para os motores da **OpenAI** (GPT-4o) ou **Google Gemini** (2.5 Flash), permitindo que a aplicação rode com altíssima precisão ou com 100% de custo zero através da chave configurável no ambiente.
- **RAG (Retrieval-Augmented Generation)**: Vetorização e busca semântica ultrarrápida hospedada no Qdrant Cloud.
- **Agente de Fallback**: Integração nativa de *Tool Calling* para pesquisa na Web usando o `langchain.agents` universal.
- **Design Imersivo (Glassmorphism)**: Interface Premium em React e TailwindCSS com Dark Mode elegante, utilitários de vidro fosco translúcido e animações modernas.
- **Automação de QA (BrowserUse)**: Scripts de teste integrados que engatilham um robô inteligente pelo navegador para validar sozinhos se a interface e as respostas da IA estão funcionais (`run_qa.py`).

## 🛠️ Stack de Tecnologias

- **Frontend**: React (Vite) + TailwindCSS
- **Backend**: Python 3.9+ + FastAPI + Uvicorn
- **Inteligência Artificial**: LangChain, LangChain Google GenAI, LangChain OpenAI
- **Banco de Dados (VectorDB)**: Qdrant
- **Deploy**: Vercel (Frontend) & Render (Backend via Blueprint)

---

## 🚀 Como rodar localmente

### 1. Clonando e Instalando o Backend
```bash
git clone https://github.com/ironidesflj/supportbot-qa.git
cd supportbot-qa
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurando as Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto (use o `.env.example` como base):

```env
# Escolha o motor de IA: 'gemini' (Padrão) ou 'openai'
LLM_PROVIDER=gemini
GEMINI_API_KEY=sua_chave_do_google_aistudio
OPENAI_API_KEY=

# Banco Vetorial e Web Search
QDRANT_URL=sua_url_do_qdrant_cloud
QDRANT_API_KEY=sua_chave_qdrant
QDRANT_COLLECTION_NAME=supportbot_kb_gemini
KATZILLA_API_KEY=sua_chave_katzilla_kz
```

### 3. Rodando os Servidores
Inicie o Backend:
```bash
uvicorn app.backend.main:app --reload
```

Em um novo terminal, inicie o Frontend:
```bash
cd app/frontend
npm install
npm run dev
```

---

## ☁️ Instruções de Deploy na Nuvem (Free Tier)

### Backend (Render)
1. Acesse o Render e clique em **New > Blueprint**.
2. Conecte este repositório. O arquivo `render.yaml` já está configurado com `plan: free` para bypassar a cobrança de cartão.
3. No painel do Render, vá em **Environment** e cadastre as chaves necessárias (`GEMINI_API_KEY`, `QDRANT_URL`, etc).
4. Copie a URL pública gerada para o seu backend.

### Frontend (Vercel)
1. Crie um novo projeto na Vercel importando este repositório.
2. Defina o **Root Directory** para `app/frontend`.
3. Defina o **Framework Preset** para `Vite`.
4. Em **Environment Variables**, crie uma variável chamada `VITE_API_URL` com o link público gerado pelo Render no passo anterior.
5. Faça o Deploy.

---

## 🤖 Rodando o Robô Avaliador (QA Tester)

Para testar o fluxo de ponta a ponta sem interagir com o site manualmente, você pode invocar o Agente de Browser (*BrowserUse*):

Certifique-se de configurar as variáveis de ambiente `BROWSER_USE_API_KEY` e `QA_START_URL` no seu arquivo `.env`.

```bash
python3 run_qa.py
```

O script irá criar uma tarefa no Browser-Use Cloud apontando para a sua `QA_START_URL` (se estiver rodando localmente, use uma ferramenta como ngrok ou cloudflared para gerar a URL pública). O script exibirá um link para você acompanhar o robô ao vivo interagindo com a sua aplicação e emitindo o laudo final de Qualidade.
