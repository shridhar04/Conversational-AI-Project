from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from conversational_agent.services.retrieval_service import RetrievalService

class RetrievealInput(BaseModel):
    query: str = Field(..., description="User question to search in knowledge base")

def build_retrieve_tool(retrieval_service:RetrievalService) -> StructuredTool:
    def _retrieve(query:str) -> str:
        docs = retrieval_service.search(query)
        if not docs:
            return "No relevant context found."

        lines: list[str] = []
        for doc in docs:
            source = doc.metadata.get("source_id","unknown")
            lines.append(f"[source={source} score={doc.score:.4f}] {doc.text}")

        return "\n\n".join(lines)

    return StructuredTool.from_function(
        name="search_knowledge_base",
        description=(
            "Searches the internal Pinecone knowledge base and returns relevant snippets. "
            "Use this before drafting a final answer for factual questions."
        ),
        func=_retrieve,
        args_schema=RetrieveInput,
    )        