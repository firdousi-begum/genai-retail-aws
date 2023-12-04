"""Helper utilities for working with Amazon Bedrock from Python notebooks"""
# Python Built-Ins:
import os
import json
from typing import Optional

# External Dependencies:
import boto3
from botocore.config import Config
from utils import config
from langchain.llms.bedrock import Bedrock
from typing import Optional, List, Any
from langchain.callbacks.manager import CallbackManagerForLLMRun
import base64
from PIL import Image
from io import BytesIO

# logger = logging.getLogger('retail_genai')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())


class BedrockAssistant():
    def __init__(self, modelId, logger = None):
        self.b_endpoint, self.b_region = config.getBedrockConfig()
        self.key, self.secret, self.region, self.sessionToken = config.getEnvCredentials()
        self.modelId = modelId
        self.logger = logger
        self.token_expiration = None
        self.boto3_bedrock = self.get_bedrock_client(
            region=self.b_region,
        )

    #print(f'Access Ke: {key}, secret: {secret}')

    def get_bedrock_client(self,
        assumed_role: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        region: Optional[str] = 'us-west-2',
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        runtime: Optional[bool] = True,
    ):
        """Create a boto3 client for Amazon Bedrock, with optional configuration overrides

        Parameters
        ----------
        assumed_role :
            Optional ARN of an AWS IAM role to assume for calling the Bedrock service. If not
            specified, the current active credentials will be used.
        endpoint_url :
            Optional override for the Bedrock service API Endpoint. If setting this, it should usually
            include the protocol i.e. "https://..."
        region :
            Optional name of the AWS Region in which the service should be called (e.g. "us-east-1").
            If not specified, AWS_REGION or AWS_DEFAULT_REGION environment variable will be used.
        """

        #print(f'Keys: Access Key ID: {aws_access_key_id}, Secret: {aws_secret_access_key}, Region: {region}, Endpoint: {endpoint_url}')


        region = self.b_region if region is None else region
        endpoint_url = self.b_endpoint 
        aws_access_key_id = self.key if aws_access_key_id is None else aws_access_key_id
        aws_secret_access_key = self.secret if aws_secret_access_key is None else aws_secret_access_key 
        aws_session_token = self.sessionToken if aws_session_token is None else aws_session_token 

        #assumed_role = 'arn:aws:iam::961655544410:role/FibegBedrockAccess'

        if region is None:
            target_region = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION"))
        else:
            target_region = region

        print(f'Keys: Access Key ID: {aws_access_key_id}, Secret: {aws_secret_access_key}, Region: {target_region}, Endpoint: {endpoint_url}')


        print(f"Create new client\n  Using region: {target_region}")
        if aws_access_key_id == '' or aws_secret_access_key == '':
            session_kwargs = {"region_name": target_region,  "aws_session_token": aws_session_token}
        else:
            session_kwargs = {"region_name": target_region, "aws_access_key_id" : aws_access_key_id, "aws_secret_access_key" : aws_secret_access_key, "aws_session_token": aws_session_token}
        client_kwargs = {**session_kwargs}


        # profile_name = os.environ.get("AWS_PROFILE")
        # if profile_name:
        #     print(f"  Using profile: {profile_name}")
        #     session_kwargs["profile_name"] = profile_name

        retry_config = Config(
            region_name=target_region,
            retries={
                "max_attempts": 5,
                "mode": "standard",
            },
        )
        session = boto3.Session(**session_kwargs)

        if assumed_role:
            print(f"  Using role: {assumed_role}", end='')
            sts = session.client("sts")
            response = sts.assume_role(
                RoleArn=str(assumed_role),
                RoleSessionName="langchain-llm-1"
            )
            print(" ... successful!")
            client_kwargs["aws_access_key_id"] = response["Credentials"]["AccessKeyId"]
            client_kwargs["aws_secret_access_key"] = response["Credentials"]["SecretAccessKey"]
            client_kwargs["aws_session_token"] = response["Credentials"]["SessionToken"]

        # if endpoint_url:
        #     client_kwargs["endpoint_url"] = endpoint_url
        
        if runtime:
            service_name='bedrock-runtime'
        else:
            service_name='bedrock'

        

        bedrock_client = session.client(
            service_name=service_name,
            config=retry_config,
            **client_kwargs
        )
        
        #bedrock_client = session_n.client(service_name='bedrock-runtime')

        #bedrock_client = boto3.client('bedrock', region_name='us-east-1')

        print("boto3 Bedrock client successfully created!")
        print(bedrock_client._endpoint)
        #print(bedrock_client.list_foundation_models())
        return bedrock_client

    def generate_image(self, modelId=None, generationConfig = None, generation_type= None, negative_prompt=''):
        if generationConfig is None or generationConfig == '':
            return
        
        if modelId is None or modelId == '':
            modelId = self.modelId

        self.logger.info(f'In Bedrock GetImage with region {self.b_region}')
        accept = 'application/json'
        contentType = 'application/json'

        if generationConfig is None:
            generationConfig = {
            "numberOfImages": 1,   # Range: 1 to 5 
            "quality": "premium",  # Options: standard or premium
            "height": 768,         # Supported height list in the docs 
            "width": 1280,         # Supported width list in the docs
            "cfgScale": generationConfig.cfg_scale,       # Range: 1.0 (exclusive) to 10.0
            "seed": generationConfig.seed             # Range: 0 to 214783647
        }

        if modelId == "amazon.titan-image-generator-v1":
            print('text to image titan')
            text = generationConfig.text_prompts[0].text
            body = json.dumps( {
                "taskType": generation_type,
                "textToImageParams": {
                    "text": text,
                    "negativeText": negative_prompt
                },
                "imageGenerationConfig": {
                    "numberOfImages": 1,   # Range: 1 to 5 
                    "quality": "premium",  # Options: standard or premium
                    "height": generationConfig.height,         # Supported height list in the docs 
                    "width": generationConfig.width,         # Supported width list in the docs
                    "cfgScale": generationConfig.cfg_scale,       # Range: 1.0 (exclusive) to 10.0
                    "seed": generationConfig.seed             # Range: 0 to 214783647
                }
            })
            response = self.boto3_bedrock.invoke_model(body=body, modelId= modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response.get("body").read())
            outputImages = [Image.open(BytesIO(base64.b64decode(base64_image))) for base64_image in response_body.get("images")]
            #outputImages = response_body.get("images")
        else:
            config = {
                "text_prompts": (
                    [{"text": prompt_data.text, "weight": prompt_data.weight} for prompt_data in generationConfig.text_prompts]
                ),
                "cfg_scale": generationConfig.cfg_scale,
                "seed": generationConfig.seed,
                "steps": generationConfig.steps,
                "width": generationConfig.width,
                "height": generationConfig.height,
            }

            #print(generationConfig)
            if generationConfig.style_preset != 'NONE':
                config.update({"style_preset": generationConfig.style_preset})

            if generationConfig.clip_guidance_preset is not None:
                config.update({"clip_guidance_preset": generationConfig.clip_guidance_preset})

            if generationConfig.sampler is not None:
                config.update({"sampler": generationConfig.sampler})

            if generationConfig.mask_source is not None:
                config.update({
                    "mask_source": generationConfig.mask_source,
                    "mask_image" : generationConfig.mask_image,
                    "init_image": generationConfig.init_image,
                    })
            
            if generationConfig.init_image_mode is not None:
                config.update({
                    "init_image_mode": generationConfig.init_image_mode,
                    "init_image": generationConfig.init_image,
                    })
                
                if generationConfig.init_image_mode == "STEP_SCHEDULE":
                    config.update({
                        "step_schedule_start": generationConfig.step_schedule_start,
                        "step_schedule_end": generationConfig.step_schedule_end,
                        })
                else:
                    config.update({
                         "image_strength": generationConfig.image_strength,
                        })
            
            #print(config)

            body = json.dumps(config) 
            response = self.boto3_bedrock.invoke_model(body=body, modelId= modelId)
            response_body = json.loads(response.get("body").read())
            outputImages = [Image.open(BytesIO(base64.b64decode(base64_image.get("base64")))) for base64_image in response_body.get("artifacts")]
       
        return outputImages


    def get_text(self, prompt, modelId=None, generationConfig = None):
        if prompt is None or prompt == '':
            return
        
        if modelId is None or modelId == '':
            modelId = self.modelId

        self.logger.info(f'In Bedrock GetText with region {self.b_region}')



        accept = 'application/json'
        contentType = 'application/json'
        if generationConfig is None:
            generationConfig = {
                "maxTokenCount":4096,
                "stopSequences":[],
                "temperature":0,
                "topP":0.9
                }

        #print(f'Claude response: {response_body}')
        config = generationConfig.copy()
        if "claude" in modelId:
            print('hello')
            config.update(
                    {"prompt": f"Human: {prompt}\n\nAssistant:"}
                )
            body = json.dumps(config) 
            response = self.boto3_bedrock.invoke_model(body=body, modelId= modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response.get('body').read())
            outputText = response_body['completion']
        elif modelId == "ai21.j2-jumbo-instruct":
            config.update(
                {"prompt": {prompt}}
            )
            body = json.dumps(
              config
            ) 
            response = self.boto3_bedrock.invoke_model(body=body, modelId= modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response.get('body').read())
            # response_lines = response['body'].readlines()
            # json_str = response_lines[0].decode('utf-8')
            # json_obj = json.loads(json_str)
            # outputText = json_obj['completions'][0]['data']['text']
            outputText = response_body['completions'][0]['data']['text']
        elif modelId == "meta.llama2-13b-chat-v1":
            config.update(
                {"prompt": prompt}
            )
            body = json.dumps(
              config
            ) 
            response = self.boto3_bedrock.invoke_model(body=body, modelId= modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response.get('body').read().decode('utf-8'))
            outputText = response_body['generation'].strip()
        else:
            config.update(
                    {"inputText": {prompt}}
                )
            body = json.dumps(
               config
            ) 
            response = self.boto3_bedrock.invoke_model(body=body, modelId= modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response.get('body').read())
            outputText = response_body.get('results')[0].get('outputText')
        return outputText


    def get_text_t(self, body, modelId=None, generationConfig = None):
        if body is None or body == '':
            return
        
        if modelId is None or modelId == '':
            modelId = self.modelId

        self.logger.info('In Bedrock GetText-T')

        accept = 'application/json'
        contentType = 'application/json'
        if generationConfig is None:
            generationConfig = {
                "maxTokenCount":4096,
                "stopSequences":[],
                "temperature":0,
                "topP":0.9
                }

        # body = json.dumps({
        #     "inputText": prompt, 
        #     "textGenerationConfig": generationConfig
        #     }) 
        response = self.boto3_bedrock.invoke_model(body=body, modelId= modelId, accept=accept, contentType=contentType)
        response_body = json.loads(response.get('body').read())
        #print(f'Claude response: {response_body}')

        if "claude" in modelId:
            outputText = response_body['completion']
        elif modelId == "ai21.j2-jumbo-instruct":
            # response_lines = response['body'].readlines()
            # json_str = response_lines[0].decode('utf-8')
            # json_obj = json.loads(json_str)
            # outputText = json_obj['completions'][0]['data']['text']
            outputText = response_body['completions'][0]['data']['text']
        else:
            outputText = response_body.get('results')[0].get('outputText')

        return outputText

class BedrockModelClaudeWrapper(Bedrock):
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        prompt = "\n\nHuman: " + prompt + "\n\nAssistant:"   ## Satisfy Bedrock-Claude prompt requirements
        return super()._call(prompt, stop, run_manager, **kwargs)




