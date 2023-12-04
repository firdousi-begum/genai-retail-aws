from typing import List
import json
from .bedrock import BedrockEmbeddingsModel


class TitanTextEmbeddings(BedrockEmbeddingsModel):

    def model_id(self) -> str:
        return "amazon.titan-embed-text-v1"
    
    def get_body(self, data: str) -> str:
        return json.dumps({
            "inputText": data
        })
    
    def parse_response(self, response: bytes) -> List[float]:
        response_body = json.loads(response.get('body').read())
        embedding = response_body.get('embedding')
        return embedding
    

class TitanTextEmbeddingsV2(BedrockEmbeddingsModel):

    def model_id(self) -> str:
        return "amazon.titan-embed-g1-text-02"
    
    def get_body(self, data: str) -> str:
        return json.dumps({
            "inputText": data
        })
    
    def parse_response(self, response: bytes) -> List[float]:
        response_body = json.loads(response.get('body').read())
        embedding = response_body.get('embedding')
        return embedding