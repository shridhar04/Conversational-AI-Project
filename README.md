# Conversational Agentic GenAI (ChatGroq + Pinecone)

Production-style starter for a conversational RAG/agentic service.

## Architecture

- API: FastAPI with health, ingest, and chat endpoints.
- LLM: ChatGroq via `langchain-groq`.
- Vector DB: Pinecone index (cosine similarity).
- Agent runtime: LangGraph ReAct agent with retrieval tool.
- Ingestion: PDF loader, text chunking, embedding, vector upsert.
- Cache memory: session memory + response cache (Redis when configured, in-memory fallback).

## Project Layout

- `src/conversational_agent/main.py`: FastAPI application entrypoint.
- `src/conversational_agent/api/routes.py`: HTTP routes.
- `src/conversational_agent/services/`: ingestion, retrieval, and chat logic.
- `src/conversational_agent/agent/`: agent graph and tools.
- `scripts/`: operational scripts for bootstrap and PDF ingestion.

## Quickstart

1. Create and activate a virtual environment.
2. Install dependencies.
3. Set environment variables.
4. Bootstrap Pinecone index.
5. Ingest PDFs.
6. Run API.

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -e .[dev]
cp .env.example .env
python scripts/bootstrap_index.py
python scripts/ingest_pdf.py --path "data/Building Machine Learning Systems with Python - Second Edition.pdf"
uvicorn conversational_agent.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /api/v1/health`
- `POST /api/v1/ingest/pdf`
- `POST /api/v1/chat`

### Example Chat Request

```json
{
  "session_id": "user-123",
  "query": "What are the key model evaluation techniques in chapter 1?"
}
```

## Production Notes

- Replace in-memory session history with Redis/Postgres.
- Tune `RESPONSE_CACHE_TTL_SECONDS` based on your freshness requirements.
- Add auth (JWT/OAuth2) and request quotas.
- Add tracing/metrics (OpenTelemetry + Prometheus).
- Add background ingestion queue (Celery/Arq).
- Add blue/green deployment and secrets manager integration.
