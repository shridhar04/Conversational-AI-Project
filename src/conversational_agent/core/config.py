from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Conversational Agentic GenAI API", alias="APP_NAME")
    app_env: str = Field(default="dev", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    backend_provider: str = Field(default="aws", alias="BACKEND_PROVIDER")
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")

    groq_api_key: str = Field(alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")

    pinecone_api_key: str = Field(alias="PINECONE_API_KEY")
    pinecone_index_name: str = Field(default="conversation-rag-index", alias="PINECONE_INDEX_NAME")
    pinecone_namespace: str = Field(default="default", alias="PINECONE_NAMESPACE")
    pinecone_cloud: str = Field(default="aws", alias="PINECONE_CLOUD")
    pinecone_region: str = Field(default="us-east-1", alias="PINECONE_REGION")

    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL"
    )
    embedding_dimension: int = Field(default=384, alias="EMBEDDING_DIMENSION")
    aws_bedrock_chat_model_id: str = Field(
        default="anthropic.claude-3-5-sonnet-20241022-v2:0",
        alias="AWS_BEDROCK_CHAT_MODEL_ID",
    )
    aws_bedrock_embedding_model_id: str = Field(
        default="amazon.titan-embed-text-v2:0",
        alias="AWS_BEDROCK_EMBEDDING_MODEL_ID",
    )
    aws_opensearch_endpoint: str | None = Field(default=None, alias="AWS_OPENSEARCH_ENDPOINT")
    aws_opensearch_index_name: str = Field(
        default="conversation-rag-index", alias="AWS_OPENSEARCH_INDEX_NAME"
    )

    top_k: int = Field(default=5, alias="TOP_K")
    chunk_size: int = Field(default=1000, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=120, alias="CHUNK_OVERLAP")
    semantic_similarity_threshold: float = Field(
        default=0.72, alias="SEMANTIC_SIMILARITY_THRESHOLD"
    )
    semantic_max_chunk_chars: int = Field(default=1600, alias="SEMANTIC_MAX_CHUNK_CHARS")
    semantic_max_sentences_per_chunk: int = Field(
        default=8, alias="SEMANTIC_MAX_SENTENCES_PER_CHUNK"
    )

    redis_url: str | None = Field(default=None, alias="REDIS_URL")
    session_ttl_seconds: int = Field(default=86400, alias="SESSION_TTL_SECONDS")
    response_cache_ttl_seconds: int = Field(default=1800, alias="RESPONSE_CACHE_TTL_SECONDS")

    auth_secret_key: str = Field(default="change_this_to_a_long_random_secret", alias="AUTH_SECRET_KEY")
    auth_algorithm: str = Field(default="HS256", alias="AUTH_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    auth_users_json: str = Field(
        default='[{"username":"admin","password":"admin123","roles":["admin","writer","reader"]}]',
        alias="AUTH_USERS_JSON",
    )

    otel_enabled: bool = Field(default=True, alias="OTEL_ENABLED")
    otel_service_name: str = Field(default="conversational-agentic-genai", alias="OTEL_SERVICE_NAME")
    otel_exporter_otlp_endpoint: str | None = Field(default=None, alias="OTEL_EXPORTER_OTLP_ENDPOINT")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
