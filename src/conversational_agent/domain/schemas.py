from typing import Any

from pydantic import BaseModel, Field

class Healthresponse(BaseModel):
    status: str = "ok"

class IngestPDFRequest(BaseModel):
    path: str = Field(..., description="Absolute or relative path to PDF")
    source_id: str | None = Field(default=None, description="Optional source identifier")


class IngestResponse(BaseModel):
    source_id: str
    chunks_ingested: int


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)


class SourceSnippet(BaseModel):
    id: str
    score: float
    metadata: dict[str, Any]
    text: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceSnippet]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"