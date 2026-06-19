# Tradeoff Analysis & Lessons Learned

## 1. Custom LLM-as-a-Judge vs. Off-the-shelf Frameworks
**Tradeoff:** Building custom evaluation metrics from scratch required writing robust JSON parsers and handling LLM flakiness (e.g., models wrapping JSON in markdown). We could have used Ragas or DeepEval.
**Lesson:** For a portfolio project targeting Senior/Staff AI Engineer roles, custom metrics prove a deep understanding of how LLMs evaluate text. The effort to handle JSON parsing exceptions and strict prompt engineering for the judge was worth the demonstrable skill.

## 2. Hardcoded Fallback vs. LLM-driven Refusal
**Tradeoff:** We implemented a hardcoded fallback string when the Qdrant similarity threshold is not met, bypassing the LLM entirely. 
**Lesson:** Relying on the LLM to decide when to refuse based on empty context often leads to occasional hallucinations ("creativity"). A deterministic, code-level hard stop guarantees 100% refusal behavior when context is missing, drastically improving the `RefusalMetric` scores and system safety.

## 3. Sync vs Async in RAG Components
**Tradeoff:** While FastAPI is async, the LangChain Qdrant and OpenAI clients have varying levels of native async support depending on the version.
**Lesson:** To ensure accurate latency measurements without overcomplicating the thread pool execution, we kept the core RAG logic synchronous but wrapped it in FastAPI's async handlers. In a high-throughput production system, migrating entirely to `AsyncOpenAI` and async Qdrant clients would be the next optimization step.
