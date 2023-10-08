import boto3
import json
import time

from attrs import define, field, Factory
from botocore.eventstream import EventStream
from typing import Any, List, Dict, Iterable, Literal, overload, Callable
import logging

from abc import abstractmethod

logger=logging.getLogger(__name__)

class StreamingResponse(Iterable):
    def __init__(self, source: Iterable, parser: Callable[[Dict[str, Any]], str]):
        self.source = iter(source)
        self.parser = parser
    
    def __next__(self) -> List[str]:
        el = json.loads(next(self.source)["chunk"]["bytes"])
        return self.parser(el)

    def __iter__(self) -> Iterable:
        return self

@define(kw_only=True)
class StreamDetails:
    stream: Iterable = field(default=None)
    prompt: str = field(default="")
    body: str = field(default="")
    latency: float = field(default=0.0)

@define(kw_only=True)
class CompletionDetails:
    output:str = field(default="")
    response: Dict[str, any] = field(factory=dict)
    prompt: str = field(default="")
    body: str = field(default="")
    latency: float = field(default=0.0)

@define(kw_only=True)
class BedrockFoundationModel:
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

    @overload
    def generate(
        self,
        prompt: str,
        *,
        top_p: float = None,
        temperature: float = None,
        token_count: int = None,
        stop_words: List[str] = [],
        extra_args: Dict[str, Any] = None,
        details: Literal[True],
        stream: Literal[True],
    ) -> StreamDetails:
        ...

    @overload
    def generate(
        self,
        prompt: str,
        *,
        top_p: float = None,
        temperature: float = None,
        token_count: int = None,
        stop_words: List[str] = [],
        extra_args: Dict[str, Any] = None,
        details: Literal[True],
        stream: Literal[False],
    ) -> CompletionDetails:
        ...

    @overload
    def generate(
        self,
        prompt: str,
        *,
        top_p: float = None,
        temperature: float = None,
        token_count: int = None,
        stop_words: List[str] = [],
        extra_args: Dict[str, Any] = None,
        details: Literal[False],
        stream: Literal[False],
    ) -> List[str]:
        ...

    @overload
    def generate(
        self,
        prompt: str,
        *,
        top_p: float = None,
        temperature: float = None,
        token_count: int = None,
        stop_words: List[str] = [],
        extra_args: Dict[str, Any] = None,
        details: Literal[False],
        stream: Literal[True],
    ) -> Iterable:
        ...


    def generate(
        self,
        prompt: str,
        *,
        top_p: float = None,
        temperature: float = None,
        token_count: int = None,
        stop_words: List[str] = [],
        extra_args: Dict[str, Any] = None,
        details: bool = False,
        stream: bool = False,
    ) -> StreamDetails | CompletionDetails | List[str] | Iterable:

        """Generates a response from the model based on the prompt and the additional optional arguments

        Args:
            prompt (str): the text prompt
            top_p (float, optional): The Top P value. Defaults to the value set on the model instance.
            temperature (float, optional): The temperature for the generation. Defaults to the value set on the model instance.
            token_count (int, optional): Max number of tokens to return. Defaults to the value set on the model instance.
            stop_words (List[str], optional): The list of stop words. Defaults to the value set on the model instance.
            extra_args (Dict[str, Any], optional): Model specific extra arguments. Defaults to the value set on the model instance.
            
        Returns:
            Dict[str, Any]: A dictionary containing the output from the model as Dictionary, the prompt, the body passed to the model an the inference time.
        """
        if extra_args is None:
            extra_args = dict(self.extra_args)
        self.validate_extra_args(extra_args)
        logger.debug(f"extra_args = {extra_args}")
        if stop_words is None:
            stop_words = list(self.stop_words)

        logger.debug(f"stop_word = {stop_words}")
        body = self.get_body(
            prompt,
            top_p or self.top_p,
            temperature or self.temperature,
            token_count or self.token_count,
            stop_words,
            extra_args,
            stream,
        )
        logger.debug(f"Body= {body}")
        t = time.time()
        try:
            if stream:
                resp = self.client.invoke_model_with_response_stream(
                    modelId=self.model_id(),
                    body=body,
                    contentType="application/json",
                    accept="*/*",
                )
            else:
                resp = self.client.invoke_model(
                    modelId=self.model_id(),
                    body=body,
                    contentType="application/json",
                    accept="*/*",
                )
        except Exception as ex:
            raise ex

        
        if details: 
            if stream: 
               return StreamDetails(stream=resp["body"], prompt=prompt,  body=body, latency=time.time()-t)
               
            else:
                out_body = json.loads(resp["body"].read())
                return CompletionDetails(output=self.parse_response(out_body), 
                                         response=out_body, 
                                         prompt=prompt, 
                                         body=body, 
                                         latency=time.time() - t)
        else: 
            if stream:
                return StreamingResponse(resp["body"], parser=self.get_text)
            else:
                out_body = json.loads(resp["body"].read())
                return self.parse_response(out_body)

    @abstractmethod
    def get_body(
        self,
        prompt: str,
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
    client: Any = field(default=boto3.client("bedrock"), )

    @abstractmethod
    def model_id(self) -> str:
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
