from langchain_aws import ChatBedrockConverse
from langchain_groq import ChatGroq

from conversational.agents.core.config import Settings

def build_chat_model(settings: Settings) -> ChatBedrockConverse | ChatGroq:
    if settings.chat_model_provider == "aws":
        return ChatBedrockConverse(
            model=settings.aws_bedrock_chat_model_id,
            region_name=settings.aws_region,
            temperature=0.1,

        )
    return ChatGroq(api_key=settings.groq_api_key, model=settings.groq_chat_model_id, temperature=0.1)