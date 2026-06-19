# Portfolio Presentation Guide

This document guides you on how to present the "SupportBot QA" project in interviews and resume reviews.

## Elevator Pitch
"I built an enterprise-grade RAG customer support chatbot with a strong emphasis on AI Quality Assurance. Instead of just building a LangChain wrapper, I engineered a custom evaluation framework using LLM-as-a-Judge to test for faithfulness, context relevance, and prompt injection resistance, ensuring the bot meets strict latency and hallucination thresholds."

## Key Talking Points for Interviews

### 1. Architecture & Engineering
- Discuss the **Modular Monolith** design. Why separating the `eval` module from the `app` module is crucial for testing internal components without HTTP overhead.
- Explain the ingestion pipeline (PDF/MD parsing, chunking, Qdrant vector storage).

### 2. AI Quality Assurance (The Differentiator)
- Explain how the `LLMJudge` works. How did you handle malformed JSON from GPT-4?
- Discuss the datasets (Golden, Adversarial, Refusal). Why is testing refusal behavior as important as testing correct answers?
- Explain the metrics: Faithfulness, Context Relevance, Latency, Refusal.

### 3. Security & Reliability
- Talk about the **Threat Model**. How does the system resist prompt injection? (System prompt constraints + deterministic fallback).
- Explain the **Similarity Threshold** (0.75). How did you balance false positives (refusing valid questions) vs. false negatives (allowing bad context)?

### 4. DevOps & CI/CD
- Highlight the GitHub Actions pipeline. Linting with `ruff` and automated Pytest runs.
- Discuss Docker Compose orchestration for local development (Frontend, Backend, Qdrant).

## How to Run It for Interviewers
1. Show the `docker-compose up` command spinning up the whole stack.
2. Use the Frontend UI to upload a PDF (Ingestion).
3. Ask a question in the chat, then ask an out-of-domain question to demonstrate the hardcoded fallback.
4. Open a terminal and run `pytest eval/tests/ -v` to show the LLM-as-a-Judge evaluating the pipeline in real-time.
