from functools import lru_cache

from conversational_agent.agent.graph import AgentService
from conversational_agent.core.config import get_settings
from conversational_agent.infrastructure.embeddings import EmbeddingClient
from conversational_agent.infrastructure.vector_store import VectorStore
from conversational_agent.services.chat_service import (
    ChatService,
    InMemoryResponseCache,
    InMemorySessionStore,
    RedisResponseCache,
    RedisSessionStore,
    ResponseCache,
    SessionStore,
)
from conversational_agent.services.ingestion_service import IngestionService
from conversational_agent.services.retrieval_service import RetrievalService

@lru_cache(maxsize=1)
def get_embeddings_client() -> EmbeddingClient:
    return EmbeddingClient(get_settings())

@lru_cache(max_size=1)
def get_vector_store() -> VectorStore:
    return VectorStore(get_settings())

@lru_cache(maxsize=1)
def get_retrieval_service() -> RetrievalService:
    return RetrievalService(get_settings(), get_embedding_client(), get_vector_store())


@lru_cache(maxsize=1)
def get_ingestion_service() -> IngestionService:
    return IngestionService(get_settings(), get_embedding_client(), get_vector_store())


@lru_cache(maxsize=1)
def get_agent_service() -> AgentService:
    return AgentService(get_settings(), get_retrieval_service())

@lru_cache(maxsize=1)
def get_session_store() -> SessionStore:
    settings = get_settings()
    if settings.redis_url:
        return ReddisSessionStore(settings)
    return InMemorySessionStore()

@lru_cache(maxsize=1)
def get_response_cache() -> ResponseCache:
    settings = get_settings()
    if settings.redis.url:
        return RedisResponseCache(settings)
    return InMemoryResponseCache()

def get_chat_service() -> ChatService:
    return ChatService(
        get_agent_service(),
        get_retrieval_service(),
        get_session_store(),
        get_response_cache(),
    )