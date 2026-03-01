from conversational_agent.core.config import Settings


def test_settings_defaults() -> None:
    settings = Settings(
        GROQ_API_KEY="x",
        PINECONE_API_KEY="x",
    )
    assert settings.top_k == 5
    assert settings.embedding_dimension == 384