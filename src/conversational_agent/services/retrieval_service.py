from conversational_agent.core.config import Settings
from conversational_agent.domain.schemas import SourceSnippet
from conversational_agent.infrastructure.embeddings import EmbeddingClient
from conversational_agent.infrastructure.vector_store import VectorStore


class RetrievalService:
    def __init__(
        self,
        settings: Settings,
        embeddings: EmbeddingClient,
        vector_store: VectorStore,
    ) -> None:
        self._settings = settings
        self._embeddings = embeddings
        self._vector_store = vector_store

    def search(self, query: str) -> list[SourceSnippet]:
        query_vector = self._embeddings.embed_query(query)
        matches = self._vector_store.query(query_vector, top_k=self._settings.top_k)

        sources: list[SourceSnippet] = []
        for match in matches:
            metadata = dict(match.metadata or {})
            text = str(metadata.get("text", ""))
            sources.append(
                SourceSnippet(
                    id=str(match.id),
                    score=float(match.score or 0.0),
                    metadata=metadata,
                    text=text,
                )
            )
        return sources
