from pathlib import Path
from uuid import uuid4

from pypdf import PdfReader

from conversational_agent.core.config import Settings
from conversational_agent.infrastructure.embeddings import EmbeddingClient
from conversational_agent.infrastructure.vector_store import VectorStore
from conversational_agent.utils.text import chunk_text

class IngestionService:
    def __init__(
            self,
            settings:Settings,
            embeddings:EmbeddingClient,
            vector_store:VectorStore,
    ) -> None:
        self._settings = settings
        self._embeddings = embeddings
        self._vectorstore = vector_store

    def ingest_pdf(self,pdf_path: str, source_id:str | None = None) -> tuple[str, int]:
        path = Path(pdf_path)
        if not path.exists() path.suffix.lower() != ".pdf":
           raise ValueError(f"Invalid PDF path: {pdf_path}")   

        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages ]
        full_text = '\n'.join(pages).strip()
        if not full_text:
            raise ValueError("PDF contains no extractable text")

        chunks = chunk_text(
            full_text,
            chunk_size=self._settings.chunk_size,
            chunk_overlap=self._settings.chunk_overlap,
        )
        if not chunks:
            raise ValueError("No chunks generated from PDF")

        embeddings = self._embeddings.embed_documents(chunks)
        resolved_source_id = source_id or path.stem

        payload = []
        for idx, (text, vector) in enumerate(zip(chunks, embeddings, strict=True)):
            vector_id = f"{resolved_source_id}-{idx}-{uuid4().hex[:8]}"
            payload.append(
                {
                    "id": vector_id,
                    "values":vector,
                    "metadata":{
                        "source_id":resolved_source_id,
                        "chunk_index":idx,
                        "text":text,
                        "path":str(path),
                    }
                }
            )
        self._vector_store.upsert(payload)
        return resolved_source_id, len(payload)
