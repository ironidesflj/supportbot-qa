# SupportBot QA 🤖

![React](https://img.shields.io/badge/React-18-20232a?style=for-the-badge&logo=react&logoColor=61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-005571?style=for-the-badge&logo=fastapi)
![LangChain](https://img.shields.io/badge/LangChain-0.1-121212?style=for-the-badge)
![Qdrant](https://img.shields.io/badge/Qdrant-1.10-f90b49?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Google_Gemini-2.5-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

An advanced **AI support system (RAG)** focused on Quality Assurance. Administrators upload knowledge bases (PDFs or texts) and interact with the content through an intelligent chatbot.

When the answer is not in the vectorized documents, the system has an **Autonomous Fallback Agent** (Function Calling) that searches the web in real time using the Katzilla API.

## 🌟 Key Features

- **Hybrid Multi-Model Architecture**: Dynamic support for **Google Gemini** (2.5 Flash, default) or **OpenAI** (GPT-4o), configurable via environment variables.
- **RAG (Retrieval-Augmented Generation)**: Vectorization and semantic search powered by Qdrant Cloud.
- **Direct Gemini SDK Integration**: Custom `DirectGeminiEmbeddings` class bypasses the buggy `langchain-google-genai` wrapper for reliable embeddings with `gemini-embedding-001` (3072 dims).
- **Per-Model Similarity Thresholds**: Auto-detects optimal threshold based on embedding model (no more hardcoded 0.75 cutting valid results).
- **Web Search Fallback**: Native Tool Calling integration for real-time web search via Katzilla when KB context is insufficient.
- **Production-Ready Backend**: Lifespan singletons, async I/O via `run_in_threadpool`, structured JSON logging, rate limiting (slowapi), optional API key auth on `/api/ingest`.
- **Accessibility-First Frontend**: ARIA-compliant tabs, live regions for screen readers, keyboard navigation, drag-and-drop file upload.
- **Custom Evaluation Framework**: LLM-as-a-Judge metrics (faithfulness, context relevance, refusal behavior, latency) with golden, adversarial, and refusal datasets.
- **Real CI/CD**: GitHub Actions with Qdrant service container, automated eval runs, Ruff linting.

## 🛠️ Tech Stack

- **Frontend**: React 18 (Vite) + TailwindCSS (glassmorphism dark theme)
- **Backend**: Python 3.9+ + FastAPI + Uvicorn
- **AI**: LangChain, Google Gemini (direct SDK), OpenAI (optional)
- **Vector DB**: Qdrant (local Docker or Qdrant Cloud)
- **Eval**: Pytest + custom LLM-as-a-Judge
- **Deploy**: Vercel (frontend) + Render (backend)

---

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│    Qdrant    │     │   Gemini    │
│  (Vercel)   │ API │  (Render)   │     │    Cloud     │     │    API      │
│  React/Vite │     │  FastAPI    │     │  3072 dims   │     │  embedding  │
└─────────────┘     └─────┬───────┘     └──────────────┘     │  + chat     │
                          │                                   └─────────────┘
                          │ fallback (no context)
                          ▼
                   ┌─────────────┐
                   │  Katzilla   │  (web search agent)
                   │   API       │
                   └─────────────┘
```

### Key Design Decisions

1. **DirectGeminiEmbeddings** (`app/rag/embeddings.py`): Custom LangChain `Embeddings` implementation that calls `google.generativeai.embed_content()` directly, bypassing the `langchain-google-genai` wrapper which was returning 504 errors (masking 404s) with the new `gemini-embedding-*` model family.

2. **Per-Model Thresholds** (`app/rag/thresholds.py`): Lookup table with optimal cosine similarity thresholds per embedding model. Override via `SIMILARITY_THRESHOLD` env var still works.

3. **Lifespan Singletons**: `Retriever`, `Generator`, and `IngestionPipeline` instantiated once on FastAPI startup (not per-request), eliminating redundant Qdrant/Gemini client creation.

4. **Async I/O**: Sync LangChain calls wrapped with `run_in_threadpool` to avoid blocking the FastAPI event loop.

5. **Hardcoded Refusal**: When context is empty AND no Katzilla fallback is configured, the system returns a deterministic refusal message (bypassing the LLM entirely) — 100% refusal behavior, zero hallucination risk.

---

## 🚀 Quick Start (Local)

### 1. Clone and Install Backend

```bash
git clone https://github.com/ironidesflj/supportbot-qa.git
cd supportbot-qa
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> **Note**: Python 3.10+ recommended. The project works on 3.9 but Google deprecates 3.9 support.

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

Required variables:
- `GEMINI_API_KEY` — Get yours at [Google AI Studio](https://aistudio.google.com/apikey)
- `QDRANT_URL` + `QDRANT_API_KEY` — Get yours at [Qdrant Cloud](https://cloud.qdrant.io) (free tier available)

Optional:
- `KATZILLA_API_KEY` — Enable web search fallback (leave empty to disable)
- `INGEST_API_KEY` — Protect `/api/ingest` with API key auth

### 3. Download NLTK Data (one-time)

```bash
python3 -c "import nltk; nltk.download('punkt_tab'); nltk.download('averaged_perceptron_tagger_eng')"
```

### 4. Seed the Knowledge Base

```bash
python3 seed_kb.py
```

This ingests the sample documents in `docs/sample_kb/` into Qdrant. Expected output:
```
Found 2 documents to ingest:
  - billing_policy.md
  - plans_overview.md
  OK  billing_policy.md: N chunks added
  OK  plans_overview.md: N chunks added
Done. Total chunks ingested: N
```

### 5. Run the Backend

```bash
uvicorn app.backend.main:app --reload
```

Backend runs on `http://localhost:8000`.

### 6. Run the Frontend

In a new terminal:
```bash
cd app/frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000` (Vite proxy forwards `/api/*` to backend).

### 7. Test the Chat

Open `http://localhost:3000`, go to **Chat Interface**, and ask:
- "What is the standard refund window?" → Should answer "14 days" with source `billing_policy.md`
- "How many devices can stream on the Premium plan?" → Should answer "4" with source `plans_overview.md`
- "What is the capital of France?" → Should refuse (out of domain)

---

## ☁️ Deployment (Free Tier)

### Backend (Render)

1. Go to [Render](https://render.com) → **New** → **Blueprint**
2. Connect this repository. The `render.yaml` is pre-configured with `plan: free`.
3. In **Environment**, add the required keys: `GEMINI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`, etc.
4. Copy the generated public URL.

### Frontend (Vercel)

1. Go to [Vercel](https://vercel.com) → **New Project** → import this repository
2. Set **Root Directory** to `app/frontend`
3. Set **Framework Preset** to **Vite**
4. Add **Environment Variable**: `VITE_API_URL` = your Render backend URL
5. Deploy

---

## 🤖 QA Automation (Browser-Use)

The project includes an automated end-to-end QA runner using the [Browser-Use Cloud API](https://cloud.browser-use.com):

### Prerequisites

1. Get an API key at [cloud.browser-use.com](https://cloud.browser-use.com)
2. Expose your app via a public URL (deploy or use a tunnel like `cloudflared`)
3. Configure in `.env`:
```env
BROWSER_USE_API_KEY=bu_your_key
QA_START_URL=https://your-app-url.vercel.app
```

### Run

```bash
python3 run_qa.py
```

The script creates a task on the Browser-Use cloud, which launches a headless browser, navigates to your app, asks a question in the chat, and returns a structured verdict (score 1-5, what worked, issues). Watch live at the URL printed in the terminal.

> **Note**: Browser-Use free tier is limited to 10 tasks/month.

---

## 🧪 Evaluation Framework

The `eval/` directory contains a custom evaluation framework:

### Datasets (`eval/datasets/`)
- `golden_dataset.json` — Standard queries with expected answers
- `refusal_dataset.json` — Out-of-domain queries that must trigger refusal
- `adversarial_dataset.json` — Prompt injection and jailbreak attempts

### Metrics (`eval/metrics/`)
- **Faithfulness** — Is the answer fully supported by retrieved context? (LLM judge)
- **Context Relevance** — Is the retrieved context relevant to the query? (LLM judge)
- **Refusal Behavior** — Does the system refuse correctly when needed? (deterministic)
- **Latency** — End-to-end retrieval + generation time (SLA: < 10s)

### Run Eval

```bash
pytest eval/tests/ -v
```

Tests are skipped automatically if the active provider's API key is not set. In CI, they run against a live Qdrant container with the `GEMINI_API_KEY` secret.

---

## 📁 Project Structure

```
supportbot-qa/
├── app/
│   ├── backend/
│   │   └── main.py              # FastAPI app (lifespan, auth, rate limit)
│   ├── core/
│   │   ├── config.py            # Pydantic settings
│   │   └── logging.py           # JSON structured logging
│   ├── prompts/
│   │   └── system_prompt.py     # RAG system prompt
│   └── rag/
│       ├── embeddings.py        # DirectGeminiEmbeddings (bypass langchain)
│       ├── thresholds.py        # Per-model similarity thresholds
│       ├── ingestion.py         # Document loading + chunking + Qdrant upsert
│       ├── retriever.py         # Vector search + threshold filtering
│       ├── generator.py         # LLM generation + fallback orchestration
│       └── fallback_agent.py    # Katzilla web search agent
├── app/frontend/
│   ├── src/
│   │   ├── App.jsx              # Tab navigation (ARIA)
│   │   ├── components/
│   │   │   ├── Chat.jsx         # Chat UI (a11y, empty state, error handling)
│   │   │   └── Ingestion.jsx    # File upload (drag-and-drop, a11y)
│   │   └── index.css            # Glassmorphism theme
│   └── package.json
├── eval/
│   ├── datasets/                # Golden, refusal, adversarial JSON
│   ├── metrics/                 # LLM judge + latency + refusal
│   └── tests/                   # Pytest E2E suite
├── docs/
│   ├── sample_kb/               # Sample knowledge base docs
│   ├── architecture.md
│   ├── threat-model.md
│   ├── evaluation-framework.md
│   ├── lessons-learned.md
│   └── portfolio-presentation-guide.md
├── docker/
│   └── Dockerfile.backend       # Includes libmagic, poppler, tesseract
├── .github/workflows/ci.yml     # Lint + integration test (Qdrant + Gemini)
├── seed_kb.py                   # Seed Qdrant with sample docs
├── run_qa.py                    # Browser-Use QA automation
├── docker-compose.yml
├── render.yaml                  # Render blueprint
└── requirements.txt
```

---

## 🔒 Security

- **No secrets in Git**: `.env` is gitignored; history was purged of leaked keys
- **API key auth on `/api/ingest`**: Set `INGEST_API_KEY` to require `X-API-Key` header
- **Rate limiting**: 10/min on `/api/chat`, 5/min on `/api/ingest` (configurable)
- **CORS configurable**: Set `CORS_ALLOW_ORIGINS` to restrict origins
- **Prompt injection resistance**: System prompt + deterministic refusal when context is empty

See [docs/threat-model.md](docs/threat-model.md) for details.

---

## 📝 License

MIT — see [LICENSE](LICENSE).
