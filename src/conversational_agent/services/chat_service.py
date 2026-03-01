import json
import hashlib
from typing import Protocol

import redis

from conversational_agent.agent.graph import AgentService
from conversational_agent.core.config import Settings
from conversational_agent.domain.schemas import ChatResponse
from conversational_agent.services.retrieval_service import RetrievalService

class SessionStore(Protocol):
    def get(self, session_id: str) -> list[dict[str, str]]:
        ...

    def append(self, session_id: str, role: str, content: str) -> None:
        ...

class ResponseCache(Protocol):
    def get(self, key: str) -> str | None:
        ...

    def set(self, key: str, value: str) -> None:
        ...

class InMemorySessionStore(SessionStore):
    def __init__(self) -> None:
        self._sessions: dict[str, list[dict[str, str]]] = {}

    def get(self, session_id: str) -> list[dict[str, str]]:
        return self._sessions.get(session_id, [])

    def append(self, session_id: str, role: str, content: str) -> None:
        self._sessions.setdefault(session_id, []).append({"role": role, "content": content})

class RedisSessionStore(SessionStore):
    def __init__(self,settings:Settings)-> None:
        if not settings.redis_url:
          raise ValueError("Redis url is required for RedisSessionStore")
        self._redis = redis.Redis.from_url(settings.redis_url,deocde_responses=True)
        self._ttl_seconds = settings.session_ttl_seconds

    def get(self, session_id: str) -> list[dict[str, str]]:
        key = self._key(session_id)
        items = self._redis.lrange(key,0,-1)
        result: list[dict[str,str]] = []
        for item in items:
            value = json.loads(item)
            role =str(value.get("role",""))
            content = str(value.get("content",""))
            if role and content:
                rsult.append({"role":role, "content":content})
        return result

    def append(self, session_id:str, role:str, content:str) -> None:
        key = self._key(session_id)
        payload = json.dumps({"role":role,"content",content})
        self._redis.rpush(key,payload)
        self._redis.expire(key,self._ttl_seconds)

    @staticmethod
    def _key(session_id:str) -> str:
        return f"chat:session:{session_id}"

class InMemoryResponseCache(ResponseCache):
    def __init__(self) -> None:
        self._cache: dict[str,str] = {}

    def get(self,key:str)-> str | None:
        return self._cache.get(key)

    def set(self, key: str, value: str) -> None:
        self._cache[key] = value

class RedisResponseCache(Responsecache):
    def __init__(self, settings:Settings) -> None:
        if not settings.redis_url:
            raise ValueError("REDIS URL is required for RedisResponseCache")   
        self._redis = redis.Redis.from_url(settings.redis_url,decode_response=True)
        self._ttl_seconds = settings.response_cache_ttl_seconds

    def get(self, key: str) -> str | None:
        value = self._redis.get(self._key(key))
        return str(value) if value is not None else None

    def set(self, key: str, value: str) -> None:
        self._redis.set(self._key(key), value, ex=self._ttl_seconds)

    @staticmethod
    def _key(cache_key: str) -> str:
        return f"chat:response:{cache_key}"       

class ChatService:
    def __init__(
        self,
        agent_service: AgentService,
        retrieval_service: RetrievalService,
        session_store: SessionStore,
        response_cache: ResponseCache,
    ) -> None:
        self._agent_service = agent_service
        self._retrieval_service = retrieval_service
        self._session_store = session_store
        self._response_cache = response_cache

    def chat(self, session_id:str, query:str) -> ChatResponse:
        sources = self._retrieval_service.search(query)
        cache_key = self._build_cache_key(query=query,sources=sources)
        cached_answer = self._response_cache.get(cache_key)

        if cached_answer:
            self._session_store.append(session_id, "user", query)
            self._session_store.append(session_id, "assistant", cached_answer)
            return ChatResponse(answer=cached_answer,sources=sources)
        
        history = self._session_store.get(session_id)
        answer = self._agent_service.run(query=query,history=history)
        self._response_cache.set(cache_key,answer)

        self._session_store.append(session_id, "user",query)
        self._session_store.append(session_id, "assistant",answer)

        return ChatResponse(answer=answer, sources=sources)
    
    @staticmethod
    def _build_cache_key(query:str, sources:list) -> str:
        source_ids = [f"{source.id}:{source.source:.6f}" for source in sources]
        payload = f"{query.strip().lower()}|{'|'.join(source_ids)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()