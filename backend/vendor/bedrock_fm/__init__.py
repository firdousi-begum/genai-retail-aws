"""The bedrock_fm module
"""

from .titan import TitanLarge
from .claude import ClaudeInstantV1, ClaudeV1, ClaudeV2
from .ai21 import AI21Mid, AI21Ultra
from .cohere import CommandText
from .titan_embeddings import TitanTextEmbeddings, TitanTextEmbeddingsV2
from .bedrock import StreamDetails, CompletionDetails, BedrockFoundationModel
from .exceptions import BedrockInvalidModelError

__all__ =[
    "TitanTextEmbeddings", 
    "TitanTextEmbeddingsV2",
    "TitanLarge", 
    "ClaudeInstantV1",
    "ClaudeV1",
    "ClaudeV2",
    "AI21Mid", 
    "AI21Ultra",
    "StreamDetails",
    "CompletionDetails",
    "BedrockFoundationModel",
    "CommandText",
    "from_model_id"
]

__model_map = {
    TitanLarge.model_id: TitanLarge,
    ClaudeInstantV1.model_id: ClaudeInstantV1,
    ClaudeV1.model_id: ClaudeV1,
    ClaudeV2.model_id: ClaudeV2,
    CommandText.model_id: CommandText,
    AI21Mid.model_id: AI21Mid,
    AI21Ultra.model_id: AI21Ultra,
}

def from_model_id(modelId: str, **kwargs) -> BedrockFoundationModel:
    if modelId in __model_map:
        return __model_map[modelId](**kwargs)
    raise BedrockInvalidModelError(f"{modelId} is not a supported model")