# SupportBot QA — Conversational AI Testing Platform

An enterprise-grade customer-support chatbot powered by Retrieval-Augmented Generation (RAG) combined with a specialized QA and Evaluation framework for conversational AI systems.

## Objective
This project demonstrates real-world AI QA engineering skills. Unlike traditional LLM benchmarks, this project validates an entire AI product stack, testing retrieval quality, groundedness, hallucination resistance, refusal behavior, and latency.

## Tech Stack
- **Backend:** FastAPI (Python 3.11), LangChain
- **Frontend:** React, Vite, TailwindCSS
- **Vector DB:** Qdrant
- **LLMs:** OpenAI (GPT-4o-mini for generation, GPT-4o for LLM-as-a-Judge)
- **Testing/Eval:** Pytest, Custom LLM-as-a-Judge metrics

## Architecture Overview
The system is divided into two main domains: the RAG Application and the Evaluation Framework.
1. **RAG Application:** Handles document ingestion (parsing, chunking, embedding), semantic search with similarity thresholds, and context-grounded generation with strict fallback behavior.
2. **Evaluation Framework:** A Pytest-based suite that loads JSON datasets (golden, refusal, adversarial), executes the RAG pipeline, and evaluates the results using custom LLM-as-a-Judge metrics and latency checks.

## Setup & Installation
### Prerequisites
- Docker and Docker Compose installed.
- An active OpenAI API Key (required for LLM generation and LLM-as-a-Judge evaluations).

### Steps
1. Clone the repository.
2. Create a `.env` file in the root directory by copying `.env.example`.
3. Edit the `.env` file and insert your valid `OPENAI_API_KEY`.
4. Run the stack using Docker:
   ```bash
   docker-compose up --build
   ```
5. Access the frontend at `http://localhost:3000` and backend docs at `http://localhost:8000/docs`.

## Running the Evaluation Suite
The evaluation suite is a first-class feature. To run the automated tests and generate quality reports:
```bash
# Inside the backend container or local python environment
pytest eval/tests/ -v
```
