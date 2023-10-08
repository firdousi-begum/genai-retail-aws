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
import json
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
def get_product_description(features, persona):
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
    
    return titan.generate(prompt_data, temperature = 0.9,top_p=0.9 )[0].strip()

@app.route('/description',methods=['POST'], cors=True)
def generate_product_description():
    print(boto3.__version__)
    print(botocore.__version__)
    try: 
        request = app.current_request.json_body 
        print(request)
        description = ''
        
        if request:
            product_features = request["features"]
            persona = request["persona"]
            description = get_product_description(product_features, persona)
        
        return description
    except Exception as ex:
        print(traceback.format_exc(ex))
        raise BadRequestError(f"Error {ex}")