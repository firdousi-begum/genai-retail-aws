"""The langchain module
"""

from .claude import ClaudeInstantV1, ClaudeV1, ClaudeV2, ClaudeV21
from .titan_embeddings import TitanTextEmbeddings, TitanTextEmbeddingsV2, TitanTextEmbeddingsOld
from .langchain import LangChainBedrockModel
from .exceptions import BedrockInvalidModelError
from .retrievers.mongoretriever import MongoDBExtendedRetriever, MongoDBVector
from .retrievers.osretriever import OSExtendedRetriever
from .memory.dynamodb import DynamoDBMemory
from .memory.mongodb import MongoDBMemory


__all__ =[
    "TitanTextEmbeddings", 
    "TitanTextEmbeddingsV2",
    "TitanTextEmbeddingsOld",
    "ClaudeInstantV1",
    "ClaudeV1",
    "ClaudeV2",
    "ClaudeV21",
    "LangChainBedrockModel",
    "OSExtendedRetriever",
    'MongoDBExtendedRetriever',
    'DynamoDBMemory',
    'MongoDBVector',
    'MongoDBMemory',
    "from_model_id"
]

__model_map = {
    ClaudeInstantV1.model_id: ClaudeInstantV1,
    ClaudeV1.model_id: ClaudeV1,
    ClaudeV2.model_id: ClaudeV2,
    ClaudeV21.model_id: ClaudeV21,
}

def from_model_id(modelId: str, **kwargs) -> LangChainBedrockModel:
    if modelId in __model_map:
        return __model_map[modelId](**kwargs)
    raise BedrockInvalidModelError(f"{modelId} is not a supported model")