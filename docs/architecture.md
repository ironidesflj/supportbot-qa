# Architecture Overview

## High-Level Design
The architecture follows a Modular Monolith pattern. This ensures separation of concerns while keeping deployment simple via Docker Compose.

### Components
- **API Layer (`app/backend`):** Exposes REST endpoints for chat and ingestion. Handles HTTP concerns and validation.
- **RAG Domain (`app/rag`):** Contains the core business logic.
  - `IngestionPipeline`: Parses files (PDF, TXT, MD), chunks text, and upserts vectors to Qdrant.
  - `Retriever`: Queries Qdrant using vector similarity. Applies a strict threshold (>= 0.75) to filter irrelevant context.
  - `Generator`: Uses LangChain and OpenAI to generate answers. Enforces a hard fallback if context is empty.
- **Evaluation Domain (`eval`):** Independent Python package containing datasets, metrics, and tests. It imports from the RAG domain to test components in isolation.

### Data Flow (Chat)
1. User sends query to `/api/chat`.
2. `Retriever` embeds the query and searches Qdrant.
3. Context is filtered by similarity score.
4. `Generator` receives context and query. If context is empty, returns hardcoded refusal. Otherwise, prompts LLM with strict system instructions.
5. Response and sources returned to user.
