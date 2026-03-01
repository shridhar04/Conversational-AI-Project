from conversational_agent.core.config import get_settings
from conversational_agent.infrastructure.vector_store import ensure_vector_index

if __name__ == "__main__":
    settings = get_setings()
    ensure_vector_index(settings)
    print("vector index is ready")