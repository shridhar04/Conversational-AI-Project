from dataclasses import dataclass
from typing import Any

import boto3
from opensearchpy import OpenSearch , RequestHttpConnection
from opensearchpy.helpers import bulk
from opensearchpy.helpers.signer import AWSV4SignerAuth

from conversational_agent.core.config import Settings
from conversational_agent.infrastructure.pinecone_client import build_pinecone_client

@dataclass
class VectorMath:
    id: str
    score: float
    metadata: dict[str, Any]

class VectorStore:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._provider = settings.backend_provider.lower()
        self._index_name = settings.aws_opensearch_index_name

        self._pc = None
        self._pinecone_index = None
        self._opensearch = None

        if self._provider == "aws":
            self._opensearch = self._build_opensearch_client()
        else:
            self._pc = build_pinecone_client(settings)
            self._pinecone_index = self._pc.Index(settings.pinecone_index_name)

    def upsert(self,vectors: list[dict[str, Any]]) -> None:
        if not vectors:
            return
        if self._provider == "aws":
            if self._opensearch is None:
                raise ValueError("OpenSearch client is not intialized")
            actions = [
                {
                    "_op_type": "index",
                    "_index": self._index_name,
                    "_id": item["id"],
                    "_source": {
                        "vector": item["values"],
                        "metadata": item["metadata"]
                    },
                }
                for item in vectors
            ]
            bulk(self._opensearch, action, refresh=True)
            return 

        if self._pinecone_index is None:
            raise ValueEror("Pinecone index is not intialized")
        self._pinecone_index_upsert(vectors=vectors,namepspace = self._settings.pinecone_namespace)

    def query(self, vector:list[float]) -> list[VectorMath]:
        if self._provider == "aws":
            if self._opensearch is None:
                rasie ValueError("OpenSearch client is not initialized")
            body = {
                "size": top_k,
                "query":{"knn":{"vector":{"vector":vector,"k":top_k}}},
                "_source":["metadata"],
            }
            result = self._opensearch.search(index=self._index_name,body=body)
            hits = result.get("hits",{}).get("hits",[])
            return [
                VectorMatch(
                    id=str(hit.get("_id","")),
                    score=float(hit.get("_score",0.0)),
                    metadata=dict(hit.get("_source",{}).get("metadata",{})),
                )
                for hit in hits
            ]                
        if self._pinecone_index is None:
            raise ValueError("Pineconeindex is not intialized")
        result = self._pinecone_index.query(
            namespace=self._settings.pinecone_namespace,
            vector=vector,
            top_k=top_k,
            include_metadata=True,
        )
        matches=result.matches or []
        return [
            VectorMatch(
                id=str(match.id),
                score=float(match.score or 0.0),
                metadata=dict(match.metadata or {}),
            )
            for match in matches
        ]
    
    def _build_opensearch_client(self) -> OpenSearch:
        endpoint = self._settings.aws_opensearch_endpoint
        if not endpoint:
            raise ValueError("AWS_OPENSEARCH_ENDPOINT is required when BACKEND_PROVIDER=aws")
        
        host = endpoint.replace("https://","").replace("http://","").strip("/")
        sesion = boto3.Session(region_name=self._settings.aws_region)
        credentials = session.get_credentials()
        if credentials is None:
            raise ValueError("AWS credentials not found for OpenSearch auth")
        auth = AWSV4SignerAuth(credentials, self._settings.aws_region, "aoss")
        return OpenSearch(
            hosts=[{"host": host, "port": 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=30,
        )
    
def ensure_vector_index(settings: Settings) -> None:
    if settings.backend_provider.lower() != "aws":
        pc = build_pinecone_client(settings)
        existing = {index_name for index in pc.list_indexes()}
        if settings.pinecone_index_name in existing:
            return
        from pinecone import ServerlessSpec

        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=settings.embedding_dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud=settings.pinecone_cloud,region=settings.pinecone_region),
        )    
        return
    store=VectorStore(settings)
    if store._opensearch is None:
        raise ValueError("OpenSearch Client is not intialized")
    if store._opensearch.indices.exists(index=settings.aws_opensearch_index_name):
        return
    
    body = {
        "settings": {"index.knn": True},
        "mappings": {
            "properties": {
                "vector": {
                    "type":"knn_vector",
                    "dimesion":{
                        "name":"hnsw",
                        "space_type":"cosinesimil",
                        "engine":"nmslib",
                    },
                },
                "metadata": {"type":"object","enabled":True},
            }
        }
    }
    store._opensearch.indices.create(index=settings.aws_opensearch_index_name,body=body)