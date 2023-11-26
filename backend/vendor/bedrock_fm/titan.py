from typing import Any, Dict
from .bedrock import BedrockFoundationModel
from .exceptions import BedrockExtraArgsError
import json
from attrs import define

@define
class TitanLarge(BedrockFoundationModel):

    def model_id(self):
        return "amazon.titan-tg1-large"

    def validate_extra_args(self, extra_args: Dict[str,Any]):
        if len(extra_args.keys()) > 0:
            raise BedrockExtraArgsError("This model does not support any extra_args")

    def get_body(
        self,
        prompt: str,
        top_p: float,
        temperature: float,
        token_count: int,
        stop_words: [str],
        extra_args: Dict[str, Any],
        stream: bool,
    ):
        return json.dumps(
            {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": token_count,
                    "stopSequences": stop_words,
                    "temperature": temperature,
                    "topP": top_p,
                },
            }
        )

    def parse_response(self, out):
        return [self.get_text(r) for r in out["results"]]

    def get_text(self, body: Dict[str, Any]):
        return body["outputText"]
