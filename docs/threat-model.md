# Threat Model & Security Mitigations

## 1. Prompt Injection & Jailbreaks
- **Threat:** User attempts to override system instructions (e.g., "Ignore previous instructions").
- **Mitigation:** The system prompt explicitly forbids following commands that attempt to alter persona or ignore instructions. The LLM is constrained to answer ONLY based on the provided context.

## 2. Hallucinations (Ungrounded Responses)
- **Threat:** The LLM generates plausible but factually incorrect information not present in the knowledge base.
- **Mitigation:** 
  - **Retrieval Threshold:** Qdrant similarity score must be >= 0.75. If not, context is discarded.
  - **Hardcoded Fallback:** If context is empty, the `Generator` bypasses the LLM entirely and returns: *"I don’t have enough information in the knowledge base to answer that question."*

## 3. Data Leakage (System Prompt Exposure)
- **Threat:** User asks the bot to reveal its internal instructions or proprietary data.
- **Mitigation:** The system prompt contains explicit rules against revealing instructions. Furthermore, because the LLM is constrained to the retrieved context, it has no mechanism to output the system prompt unless it was ingested as a document.

## 4. Context Poisoning
- **Threat:** Malicious documents are uploaded to the knowledge base to manipulate answers.
- **Mitigation:** In V1, the `/api/ingest` endpoint is intended for administrative use only. In a production environment, this endpoint would be protected by authentication/authorization roles (RBAC), and documents would undergo a review pipeline before ingestion.
