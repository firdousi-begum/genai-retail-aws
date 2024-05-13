from typing import List
import json
from .langchain import BedrockEmbeddingsModel
from langchain.embeddings import BedrockEmbeddings

class TitanTextEmbeddingsOld(BedrockEmbeddingsModel):

    def get_llm(self):
        br_embeddings = BedrockEmbeddings(client=self.client)
        return br_embeddings

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

class TitanTextEmbeddings(BedrockEmbeddingsModel):

    def get_llm(self):
        br_embeddings = BedrockEmbeddings(client=self.client, model_id=self.model_id())
        return br_embeddings

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

    def get_llm(self):
        br_embeddings = BedrockEmbeddings(client=self.client, model_id=self.model_id())
        return br_embeddings

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