import json
import math

import boto3
from sentence_transfomers import SentneceTrasformer

from conversational_agent.core.config import Settings

class EmbeddingClient:
    def __init__(self, settings: Settings)-> None:
        self._settings = settings
        self._provider = settings.backend_provider.lower()
        self._local_model = SentenceTransformer | None = None
        self._bedrock_client = None

        if self._provider == "aws":
            self._bedrock_client = boto3.client("bedrock-runtime", region_name=settings.aws_region)
        else:
            self._local_model = SentenceTransformer(settings.embedding_model)

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        if self._provider == "aws":
            return [self._normalize(self.embed_bedrock(text)) for text in texts]
        if self._local_model is None:
            raise ValueError("Local embedding model is not intialized")
        vectors = self._local_model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()

    def _embed_query(self, text:str) -> list[float]:
        if self._provider == "aws":
            return self._normalize(self._embed_bedrock(text))
        if self._local_model is None:
            raise ValueError("Local Embedding is not intialized")
        vector = self._local_model.encode([text], normalize_embeddings=True)
        return vector[0].tolist()
    def _embed_bedrock(self, text: str) -> list[float]:
        if self_bedrock_client is None:
            raise ValueError("Bedrock runtime client is not intialized")
        body = json.dumps({"inputText": text})
        response = self._bedrock_client.invoke_model(
            modelId=self._settings.aws_bedrock_embedding_model_id,
            body=body,
            accept="application/json",
            contentType="applicaton/json", 
        )
        payload = json.loads(response["body"].read())
        vector = payload.get("embedding")
        if not isinstance(vector, list):
            raise ValueError("Bedrock embedding response missing embedding vector")
        return [float(item) for item in vector]
    
    @staticmethod
    def _normalize(vector: list[float])-> list[float]:
        norm = math.sqrt(sum(x * x for x in vector))
        if norm == 0:
            return vector
        return [x / norm for x in vector]
    