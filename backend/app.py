# Copyright 2023 Massimiliano Angelino <angmas@amazon.com>
# SPDX-License-Identifier: MIT

from chalice import Chalice, BadRequestError
from bs4 import BeautifulSoup
import requests
from bedrock_fm import ClaudeInstantV1, TitanLarge
import botocore
import boto3
import backoff
import logging
import traceback
from utils import langchain
import json
from urllib.parse import urlparse, parse_qs
logger = logging.getLogger()

app = Chalice(app_name='retail-genai')
session = boto3.Session(region_name='us-west-2')
bedrock = session.client('bedrock-runtime')
ci = ClaudeInstantV1(client=bedrock, token_count=2000, temperature=0.2)
titan = TitanLarge(client=bedrock, token_count=4096, temperature=0.2)

@app.route('/')
def index():
    return {'message': 'HELLO'}


@backoff.on_exception(backoff.expo, bedrock.exceptions.ThrottlingException)
def get_ingredients_from_list(ingredient_list):
    return ci.generate("""From the following ingredient list in swedish extract the swedish name of the ingredient, the quantity and the unit of measure for each item. 
Create a JSON document containing: the simple ingredient name in swedish, the quantity and the unit of measure. Use the fields: ingredient, quantity, unit. 
Quantity must be a number. Ingredients are nouns only. The answer contains only the JSON document.

{}""".format("\n".join([i for i in ingredient_list if i.upper() != i])))[0].strip()

@backoff.on_exception(backoff.expo, bedrock.exceptions.ThrottlingException)
def get_product_description(product_name, product_features, persona):
    persona_prompt = ''
    if persona is not None and persona != 'None':
        print(f'persona: {persona}')
        persona_prompt = f" and personalize it to persona charateristics: {persona}"

    # create the prompt
    prompt_data = f"""Product: {product_name} \
    Features: {product_features} \
    Create a detailed product description for the product listed above, {persona_prompt} \
    , the product description must \
    use at least two of the listed features.\
    """
    
    return ci.generate(prompt_data, temperature = 0.9,top_p=0.9 )[0].strip()

def generate_review_summary (product_reviews, product_name):
    
    if product_reviews is None:
        return
    
    product_reviews = f"""Product Name:{product_name}\n
    Reviews: {product_reviews}
    """
    map_prompt = """
    Write a concise summary of the following product reviews:
    "{text}"
    CONCISE SUMMARY:
    """
    map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])

    combine_prompt = """
    Write a concise summary of the following product reviews for the product delimited by triple backquotes. 
    ```{text}```

    Return overall sentiment of the product reviews in separate section 'SENTIMENT' after thie concise summary.
    Return important keywords from the product reviews in separate section 'KEYWORDS' after the 'SENTIMENT'.
    To generate concise summary, you MUST use below format:
    ```
    SUMMARY: Concise summary of the product reviews \n\n
    <b>SENTIMENT:</b> overall sentiment for the summary \n\n
    <b>KEYWORDS:</b> extract important keywords from the summary
    ```

    """
    combine_prompt_template = PromptTemplate(template=combine_prompt, input_variables=["text"])
    #modelId = 'amazon.titan-tg1-large'
    inference_config_titan = {
                            "maxTokenCount":3072,
                            "stopSequences":[],
                            "temperature":0,
                            "topP":0.9
                            }

    #print(f'Reviews:{product_reviews}')
    summary = langchain.summarize_long_text(product_reviews, modelId, inference_config_titan, map_prompt, combine_prompt)
    return summary

@app.route('/description',methods=['POST'],content_types=['application/json'], cors=True)
def generate_product_description():
    print(boto3.__version__)
    print(botocore.__version__)
    try: 
        #print(app.current_request.to_dict())
        request = app.current_request.json_body 
        print(request)
        description = ''
        
        if request:
            product_name = request["productName"]
            product_features = request["features"]
            persona = request["persona"]
            description = get_product_description(product_name, product_features, persona)

            #print(f"Description geenrated: {description}")
        
        return description
    except Exception as ex:
        print(traceback.format_exc(ex))
        raise BadRequestError(f"Error {ex}")
    
@app.route('/description',methods=['POST'],content_types=['application/json'], cors=True)
def generate_product_description():
    print(boto3.__version__)
    print(botocore.__version__)
    try: 
        #print(app.current_request.to_dict())
        request = app.current_request.json_body 
        print(request)
        description = ''
        
        if request:
            product_name = request["productName"]
            product_features = request["features"]
            persona = request["persona"]
            description = get_product_description(product_name, product_features, persona)

            #print(f"Description geenrated: {description}")
        
        return description
    except Exception as ex:
        print(traceback.format_exc(ex))
        raise BadRequestError(f"Error {ex}")