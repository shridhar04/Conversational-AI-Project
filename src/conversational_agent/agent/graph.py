from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from conversational_agent.agent.tools import build_retrieve_tool
from conversational_agent.core.config import Settings
from conversational_agent.infrastructure.llm import build_chat_model
from conversational_agent.services.retrieval_service import RetrievalService


SYSTEM_PROMPT = (
    "You are an enterprise conversational assistant. "
    "Use tools whenever retrieval is needed. build_chat_model"
    "Ground answers in retrieved context and clearly state when context is insufficient."
)

class AgentService:
    def __init__(self,settings: Settings, retrieval_service:RetrievalService) -> None:
        self._llm = build_chat_model(settings)
        self._tool = build_retrieval_tool(retrieval_service)
        self._graph = create_react_agent(self._llm, tools=[self._tool])

    def run(self, query:str, history:list[dict[str, str]]) -> str:
        messages: list[Any] = [SystemMessage(content=SYSTEM_PROMPT)]    

        for item in history:
            role = item.get("role","")
            content = item.get("content","")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))

        message.append(HumanMessage(content=query))
        result = self._graph.invoke({"messages":messages})
        final_messages = result.get("messages",[])
        if not final_messages:
            return "I could not generatea response"

        return str(final_messages[-1].content)             