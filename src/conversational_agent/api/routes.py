from fastapi import APIRouter, HTTPException

from conversational_agent.api.deps import get_chat_service, get_ingestion_service
from conversational_agent.domain.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    IngestPDFRequest,
    IngestResponse,
)

router = APIRouter(prefix="/api/v1",tags=["api"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse (status="ok")


@router.post("/ingest/pdf", response_model=IngestResponse)
def ingest_pdf(payload: IngestPDFRequest)-> IngestResponse:
    service = get_ingestion_service()
    try:
        source_id, count = service.ingest_pdf(payload.path, source_id=payload.source_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    
    return IngestResponse(source_id=source_id, chunks_ingested=count)


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    service = get_chat_service()
    return service.chat(session_id=payload.session_id, query=payload.query)