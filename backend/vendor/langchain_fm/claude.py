from .langchain import LangChainBedrockModel
from .exceptions import BedrockExtraArgsError
import json
from attrs import define
from typing import List, Any, Dict
from langchain.schema import BaseMessage


@define
class Claude(LangChainBedrockModel):
    _ROLE_MAP = {"human": "\n\nHuman: ", "ai": "\n\nAssistant: "}

    def validate_extra_args(self, extra_args: Dict[str, Any]):
        unsupp_args = []
        for k in extra_args.keys():
            if k not in ["top_k"]:
                unsupp_args.append(k)

        if len(unsupp_args) > 0:
            raise BedrockExtraArgsError(
                f"Arguments [{','.join(unsupp_args)}] are not supported by this model"
            )
    
    def get_chat_history(self,chat_history):
        buffer = ''
        for dialogue_turn in chat_history:
            #print(f"Type: {dialogue_turn.type}")
            if isinstance(dialogue_turn, BaseMessage):
                role_prefix = self._ROLE_MAP.get(dialogue_turn.type, f"{dialogue_turn.type}: ")
                buffer += f"\n{role_prefix}{dialogue_turn.content}"
            elif isinstance(dialogue_turn, tuple):
                human = "\n\nHuman: " + dialogue_turn[0]
                ai = "\n\nAssistant: " + dialogue_turn[1]
                buffer += "\n" + "\n".join([human, ai])
            else:
                raise ValueError(
                    f"Unsupported chat history format: {type(dialogue_turn)}."
                    f" Full chat history: {chat_history} "
                )
        return buffer

    def get_body(
        self,
        top_p: float,
        temperature: float,
        token_count: int,
        stop_words: List[str],
        extra_args: Dict[str, Any],
        stream: bool,
    ):
        body = extra_args.copy()
        s = list(stop_words)
        s.append("\n\nHuman:")
        body.update(
            {
                "max_tokens_to_sample": token_count,
                "stop_sequences": s,
                "temperature": temperature,
                "top_p": top_p
            }
        )
        return body


    def parse_response(self, out):
        return [self.get_text(out)]

    def get_text(self, body: Dict[str, Any]):
        return body["completion"]
    

@define
class ClaudeInstantV1(Claude):

    def model_id(self):
        return "anthropic.claude-instant-v1"

@define
class ClaudeV1(Claude):

    def model_id(self):
        return "anthropic.claude-v1"

@define
class ClaudeV2(Claude):

    def model_id(self):
        return "anthropic.claude-v2"

@define
class ClaudeV21(Claude):

    def model_id(self):
        return "anthropic.claude-v2:1"
