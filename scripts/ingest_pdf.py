import argparse

from conversational_agent.core.config import get_settings
from conversational_agent.infrastructure.embeddings import EmbeddingClient
from conversational_agent.infrastructure.vector_store import VectorStore
from conversational_agent.services.ingestion_service import IngestionService

def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest a PDF into vector store")
    parser.add_argument("--path", required=True, help="Path to PDF file")
    parser.add_argument("--source-id", required=True, help = "Optional source id override" )
    args = parser.parse_args()

    settings = get_settings()
    service = IngestionService(
        settings=settings,
        embeddings=EmbeddingClient(settings),
        vector_store=VectorStore(settings),
    )
    source_id, count = service.ingest_pdf(args.path,source_id=args.source_id)
    print(f"Ingested source id={source_id} chunks={count}")

if __name__ == "__main__":
    main()    