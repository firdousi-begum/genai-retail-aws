from .bedrock import BedrockFoundationModel
from .exceptions import BedrockExtraArgsError
import json
from typing import List, Any, Dict
from botocore.eventstream import EventStream
from attrs import define

@define
class Cohere(BedrockFoundationModel):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def validate_extra_args(self, extra_args: Dict[str, Any]):
        unsupp_args = []
        for k in extra_args.keys():
            if k not in ["return_likelihoods", "num_generations", "k"]:
                unsupp_args.append(k)

        if len(unsupp_args) > 0:
            raise BedrockExtraArgsError(
                f"Arguments [{','.join(unsupp_args)}] are not supported by this model"
            )

        # TODO: validate the content of the Penalty fields

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
        """Generate the body for Cohere models

        Args:
            prompt (str): the prompts
            top_p (float): top_p value between 0 and 1
            temperature (float): temperature between 0 and 1
            token_count (int): the number of tokens to return
            stop_words (List[str]): the list of stop words
            extra_args (Dict[str, Any]): extra args for AI21 Model

        Returns:
            _type_: _description_
        """

        body = extra_args.copy()
        body.update(
            {
                "prompt": prompt,
                "max_tokens": token_count,
                "temperature": temperature,
                "p": top_p,
                "stop_sequences": stop_words,
                "stream": stream,
            }
        )
        return json.dumps(body)

    def parse_response(self, out):
        return [self.get_text(r) for r in out["generations"]]

    def get_text(self, body: Dict[str, Any]):
        if not body.get("is_finished", False):
            t = body["text"]
            if t == "<EOS_TOKEN>":
                return "\n"
            else:
                return t
        else:
            return ""

@define
class CommandText(Cohere):
    """Create an instance of an Cohere Command Text model
    
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def model_id(self):
        return "cohere.command-text-v14"

