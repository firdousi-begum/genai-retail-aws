import boto3
import json
from langchain_community.llms import Bedrock
from langchain_community.chat_models.bedrock import BedrockChat
from attrs import define, field, Factory
from botocore.eventstream import EventStream
from typing import Any, List, Dict, Iterable, Literal, overload, Callable
import logging

from abc import abstractmethod

logger=logging.getLogger(__name__)


@define(kw_only=True)
class LangChainBedrockModel:
    """Abstract class for all foundation models exposed via Bedrock
    To add a new FM, inherit from this class and implement the abstract methods
    """
    top_p: float = field(default=1)
    temperature: float = field(default=0.7)
    token_count: int = field(default=500)
    stop_words: List[str] = field(factory=list)
    extra_args: Dict[str, Any] = field(factory=dict)
    client: Any = field(default=boto3.client("bedrock-runtime"))
  
    @abstractmethod
    def model_id(self) -> str:
        ...

    @abstractmethod
    def validate_extra_args(self, extra_args: Dict[str, Any]):
        ...
    
    @abstractmethod
    def get_chat_history(self, chat_history):
        ...

  
    def get_llm(
        self,
        top_p: float = None,
        temperature: float = None,
        token_count: int = None,
        stop_words: List[str] = [],
        extra_args: Dict[str, Any] = None,
        stream: bool = False,
        chat: bool = False,
    ) -> Any:
        if extra_args is None:
            extra_args = dict(self.extra_args)
        self.validate_extra_args(extra_args)
        logger.debug(f"extra_args = {extra_args}")
        if stop_words is None:
            stop_words = list(self.stop_words)

        logger.debug(f"stop_word = {stop_words}")
        body = self.get_body(
            top_p or self.top_p,
            temperature or self.temperature,
            token_count or self.token_count,
            stop_words,
            extra_args,
            stream,
        )

        if chat:
            llm = BedrockChat(model_id=self.model_id(), client=self.client, 
                model_kwargs = body
            )
        else:
            llm = Bedrock(model_id=self.model_id(), client=self.client, 
            model_kwargs = body
            )
        return llm

    @abstractmethod
    def get_body(
        self,
        top_p: float,
        temperature: float,
        token_count: int,
        stop_words: List[str],
        extra_args: Dict[str, Any],
        stream: bool,
    ) -> str:
        ...

    @abstractmethod
    def parse_response(self, resp) -> List[str]:
        ...

    def get_text_stream(self, stream: EventStream) -> Iterable:
        for e in stream:
            yield self.get_text(json.loads(e["chunk"]["bytes"]))

    @abstractmethod
    def get_text(self, body: Dict[str, Any]) -> str:
        ...
    

@define(kw_only=True)
class BedrockEmbeddingsModel:
    verbose: bool = field(default=False)
    client: Any = field(default=boto3.client("bedrock-runtime"))

    @abstractmethod
    def model_id(self) -> str:
        ...
    
    @abstractmethod
    def get_llm(self)-> str:
        ...

    def generate(self, data: str, *, verbose: bool = None) -> List[float]:
        body = self.get_body(data)
        verbose = verbose or self.verbose
        if verbose:
            print(body)
        response = self.client.invoke_model(
            modelId=self.model_id(),
            body=body,
            accept="*/*",
            contentType="application/json",
        )
        return self.parse_response(response)

    @abstractmethod
    def get_body(self, data: str) -> str:
        ...

    @abstractmethod
    def parse_response(self, response: bytes) -> List[float]:
        ...
