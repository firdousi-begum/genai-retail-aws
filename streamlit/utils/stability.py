# Python Built-Ins:
import os
import json
from typing import Optional
from PIL import Image
from typing import Union
import base64
from io import BytesIO

# External Dependencies:
import boto3
from botocore.config import Config
from utils import config
import sagemaker
from stability_sdk_sagemaker.predictor import StabilityPredictor
from stability_sdk.api import GenerationRequest, GenerationResponse, TextPrompt

class StabilityAssistant():
    def __init__(self, modelId, logger = None):
        self.key, self.secret, self.region, self.sessionToken = config.getEnvCredentials()
        self.modelId = modelId
        self.logger = logger
        self.token_expiration = None
        self.im_endpoint_name = modelId
        self.sm_client, self.sm_session = self.get_sagemaker_client()

    def get_sagemaker_client(self,
    assumed_role: Optional[str] = None,
    region: Optional[str] = None,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    ):
        """Create a boto3 client for Amazon Sagemaker, with optional configuration overrides

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

        region = self.region if region is None else region
        aws_access_key_id = self.key if aws_access_key_id is None else aws_access_key_id
        aws_secret_access_key = self.secret if aws_secret_access_key is None else aws_secret_access_key 
        aws_session_token = self.sessionToken if aws_session_token is None else aws_session_token 

        #assumed_role = 'arn:aws:iam::961655544410:role/FibegBedrockAccess'

        if region is None:
            target_region = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION"))
        else:
            target_region = region

        print(f'Keys: Access Key ID: {aws_access_key_id}, Secret: {aws_secret_access_key}, Region: {target_region}  ')


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

        sagemaker_client = session.client(
            service_name="sagemaker-runtime",
            config=retry_config,
            **client_kwargs
        )
        #session = boto3.session.Session(aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name=region)
        sm_session = sagemaker.Session(boto_session=session)

        print("boto3 sagemaker client successfully created!")
        print(sagemaker_client._endpoint)
        return sagemaker_client, sm_session
        
        
    def generate(self, generationRequest = None,endpoint_name=None,):
        sm_client, sm_session= self.get_sagemaker_client()
        if endpoint_name is None:
            endpoint_name = self.im_endpoint_name
        deployed_model = StabilityPredictor(endpoint_name=endpoint_name, sagemaker_session=sm_session)

        if generationRequest is None:
           return
        
        #boto3_sm = self.get_sagemaker_client()

        # accept = 'application/json'
        # contentType = 'application/json'

        # x = json.dumps(generationRequest )
        # print(type(x))
        # x = x.json(exclude_unset=True)
        # body = json.dumps(x).encode('utf-8')


        # print(f'Body: {body}')

        # response = sm_client.invoke_endpoint(EndpointName=self.im_endpoint_name, 
        #                         ContentType=contentType, 
        #                         Accept=accept,
        #                         Body=body)
        # response_body = json.loads(response['Body'].read())
        # response_body = response['Body']
        # content_type = response.get("ContentType", "application/octet-stream")
        # response_stream = self.deserializer.deserialize(response_body, content_type)

        #print(f'Response stream: {response_stream}')

        # response = deployed_model.predict(GenerationRequest(text_prompts=[TextPrompt(text="jaguar in the Amazon rainforest")],
        #                                      # style_preset="cinematic",
        #                                      seed = 12345,
        #                                     width=1024,
        #                                     height=1024.
        #                                      ))
        
        #print (f'Generation Req:{generationRequest}')
        response = deployed_model.predict(generationRequest)
       

        #print(f'Response: {response}')

        # Display generated images
        #print(f'Response: {response}')
       
        if response.artifacts:
            return [
                Image.open(
                    BytesIO(
                        base64.b64decode(base64_image.base64.encode()))
                    ) for base64_image in response.artifacts
                ]
            # return response.artifacts
        else:
            return response.result
    
    def adapt(self,
            img_str,
            prompt: str,
            negative_prompt: str = "",
            seed: int = 0,
            num_inference_steps: int = 30,
            adapter_conditioning_scale: float = 0.9,
            adapter_conditioning_factor: float = 1.0,
            guidance_scale: float = 7.5,
            endpoint_name: str= ''):
        
        #endpoint_name = 'huggingface-pytorch-inference-2023-11-12-17-36-53-941'
        #sm_client, sm_session= self.get_sagemaker_client()
        response_model = self.sm_client.invoke_endpoint(
        EndpointName=endpoint_name,
        Body=json.dumps(
            {
                "image": img_str,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "seed": seed,
                "num_inference_steps": num_inference_steps,
                "adapter_conditioning_scale": adapter_conditioning_scale,
                "adapter_conditioning_factor": adapter_conditioning_factor,
                "guidance_scale": guidance_scale,
            }
        ),
            ContentType="application/json",
        )
        return Image.open(
            BytesIO(
                base64.b64decode(
                    json.loads(response_model["Body"].read().decode("utf8"))["output_image"]
                )
            )
        )
        

