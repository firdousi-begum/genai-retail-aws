from botocore.eventstream import EventStream
from .bedrock import BedrockFoundationModel
from .exceptions import BedrockExtraArgsError
import json
from attrs import define
from typing import List, Any, Dict

@define
class Claude(BedrockFoundationModel):

    def validate_extra_args(self, extra_args: Dict[str, Any]):
        unsupp_args = []
        for k in extra_args.keys():
            if k not in ["top_k"]:
                unsupp_args.append(k)

        if len(unsupp_args) > 0:
            raise BedrockExtraArgsError(
                f"Arguments [{','.join(unsupp_args)}] are not supported by this model"
            )

    def get_body(
        self,
        prompt: str,
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
                "prompt": f"Human: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": token_count,
                "stop_sequences": s,
                "temperature": temperature,
                "top_p": top_p,
                "anthropic_version": "bedrock-2023-05-31",
            }
        )
        return json.dumps(body)

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
