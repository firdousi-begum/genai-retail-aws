# Copyright 2023 Massimiliano Angelino <angmas@amazon.com>
# SPDX-License-Identifier: MIT

from chalice import Chalice, BadRequestError
from bs4 import BeautifulSoup
import requests
from bedrock_fm import ClaudeInstantV1
import botocore
import boto3
import backoff
import logging
import traceback
import json
logger = logging.getLogger()

app = Chalice(app_name='recipes')
session = boto3.Session(region_name='us-west-2')
bedrock = session.client('bedrock-runtime')
ci = ClaudeInstantV1(client=bedrock, token_count=2000, temperature=0.2)

@app.route('/')
def index():
    return {'message': 'HELLO'}


@backoff.on_exception(backoff.expo, bedrock.exceptions.ThrottlingException)
def get_ingredients_from_list(ingredient_list):
    return ci.generate("""From the following ingredient list in swedish extract the swedish name of the ingredient, the quantity and the unit of measure for each item. 
Create a JSON document containing: the simple ingredient name in swedish, the quantity and the unit of measure. Use the fields: ingredient, quantity, unit. 
Quantity must be a number. Ingredients are nouns only. The answer contains only the JSON document.

{}""".format("\n".join([i for i in ingredient_list if i.upper() != i])))[0].strip()

@app.route('/get_products', cors=True)
def get_matching_products():
    print(boto3.__version__)
    print(botocore.__version__)
    try: 
        recipe_url=app.current_request.query_params["url"]
        resp = requests.get(recipe_url)
        bd = BeautifulSoup(resp.content)
        doc = bd.find(string="Ingredienser").parent.parent
        items=[]
        for p in doc.select('p'):
            items += p.getText().split('\n')
        print("Getting ingredients")
        ingredients = json.loads(get_ingredients_from_list(items))
        search = "https://www.hemkop.se/search?size=30&page=0&q={query}&sort=relevance"

        match_prod = []
        print(ingredients)
        for i in ingredients:
            resp = requests.get(search.format(query=i["ingredient"]))
            results = json.loads(resp.content)["results"]
            if results is not None:
                prod = results[0] 
                match_prod.append({"ingredient": i["ingredient"], "product": prod, "quantity": i["quantity"], "unit": i["unit"] })
            else: 
                match_prod.append({"ingredient": i["ingredient"], "product": None})
        
        return match_prod
    except Exception as ex:
        print(traceback.format_exc(ex))
        raise BadRequestError(f"Error {ex}")