# Copyright 2023 Massimiliano Angelino <angmas@amazon.com>
# SPDX-License-Identifier: MIT

from chalice import Chalice, BadRequestError
from bedrock_fm import ClaudeV2, BedrockService, ClaudeV21, from_model_id
import boto3
import logging
import backoff
from chalicelib.shopping_agent import ShoppingAssistant
from chalicelib.summarize import SummarizeAssistant
from urllib.parse import urlparse, parse_qs
import json
import langchain
logger = logging.getLogger()

app = Chalice(app_name='genai-retail')
session = boto3.Session(region_name='us-west-2')
bedrock = session.client('bedrock-runtime')
bedrock_service = session.client('bedrock')
cd2 = ClaudeV2(client=bedrock, token_count=4096, temperature=0, top_p=0.9)
cd21 = ClaudeV21(client=bedrock, token_count=2000, temperature=0.2)
br_service = BedrockService(client=bedrock_service)
assistant = ShoppingAssistant(client = bedrock, logger= logger)
summarize = SummarizeAssistant(client=bedrock, logger=logger)


@app.route('/')
def index():
    print(app.current_request.to_dict())
    return {'message': 'HELLO'}

@app.route('/bedrock/models', methods=['GET'])
@backoff.on_exception(backoff.expo, bedrock.exceptions.ThrottlingException)
def getBedrockModels():
    # Access query parameters from the event object
    provider = app.current_request.query_params.get('provider')
    customization_type = app.current_request.query_params.get('customization_type')
    output_modality = app.current_request.query_params.get('output_modality')
    inference_type = app.current_request.query_params.get('inference_type')

    try:
        models = br_service.get_model_list(
            provider=provider,
            customizationType=customization_type,
            outputModality=output_modality,
            inferenceType=inference_type
        )

        return models
    except Exception as e:
        return str(e)

@app.route('/products/qa')
def product_QA():
    #langchain.debug=True
    logger.info('Before')
    print('Before')
    # Access query parameters from the event object
    prompt = app.current_request.query_params.get('prompt')
    print(prompt)
    logger.info(prompt)
    try:
        print('got assistant')
        #answer = assistant.product_qa({"query": prompt})
        answer = assistant.product_qa_chain({"question": prompt})


        return answer
    except Exception as e:
        return str(e)
    
@app.route('/products/chat')
def product_chat():
    langchain.debug=True
    logger.info('Before')
    print('Before')
    # Access query parameters from the event object
    prompt = app.current_request.query_params.get('prompt')
    session_id = app.current_request.query_params.get('sid')
    print(prompt)
    logger.info(prompt)
    try:
        print('got assistant chat')
        #answer = assistant.product_qa({"query": prompt})
        answer = assistant.get_product_chat(query=prompt, session_id=session_id)

        return answer
    except Exception as e:
        print('Error')
        print(str(e))
        return str(e)
    
@app.route('/products/chat/messages')
def product_chat_messages():
    langchain.debug=True
    logger.info('Before')
    print('Before')
    session_id = app.current_request.query_params.get('sid')
    try:
        print('got assistant chat messages')
        #answer = assistant.product_qa({"query": prompt})
        messages = assistant.mongo_mem.get_messages( session_id=session_id)
        print(messages)
        return messages
    except Exception as e:
        print('Error')
        print(str(e))
        return str(e)

@app.route('/generate', methods=['POST'])
@backoff.on_exception(backoff.expo, bedrock.exceptions.ThrottlingException)
def generateText():

    # Access the current request object
    current_request = app.current_request

    # Read body parameters from the POST request
    body_params = current_request.json_body  # Assumes the body contains JSON data

    # Access specific parameters
    prompt = body_params.get('prompt')

    try:
        output = cd21.generate(prompt)

        return output
    except Exception as e:
        return str(e)
    
@app.route('/summarize/reviews', methods=['POST'])
@backoff.on_exception(backoff.expo, bedrock.exceptions.ThrottlingException)
def summarizeReviews():

    print('summarize api')
    # Access the current request object
    current_request = app.current_request

    # Read body parameters from the POST request
    body_params = current_request.json_body  # Assumes the body contains JSON data
    
    # Access specific parameters
    product_reviews = body_params.get('product_reviews')
    product_name = body_params.get('product_name')

    reviews = f"""Product Name:{product_name}\n
    Reviews: {product_reviews}
    """

    system_prompt = "You are a product analyst that summarizes the product reviews."
    
    combine_prompt = """
    Generate summary about the reviews for [Product Name] based on Product reviews delimited by triple backquotes.
    ```{text}```

    Also return overall_sentiment as 'POSITIVE', 'NEGATIVE' or 'MIXED' based on the generated summary, 
    and generate maximum 5 most important keywords for the the given product reviews and based on reviews generate sentiment for each keyword. 
    The output should ALWAYS be valid JSON document with text inside the 'outputFormat' below, do NOT add any text in the output before JSON . 
    Don't include any preamble.
    <outputFormat>
        {{
            "product_reviews_summary": "Maximum 200 words summary.",
            "overall_sentiment": "POSITIVE or NEGATIVE or MIXED",
            "keywords_highlight": [
                {{"keyword": "Quality", "sentiment": "POSITIVE"}},
                {{"keyword": "Affordability", "sentiment": "NEGATIVE"}},
                {{"keyword": "Customer Service", "sentiment": "MIXED"}}
            ]
        }}
    </outputFormat>
    """

    try:
        output = summarize.summarize_long_text(reviews, system_prompt, combine_prompt)
        print(output)

        # Claude v2.1 always returns text with json

        # Find the index of the first '{' and the last '}'
        start_idx = output.index('{')
        end_idx = output.rindex('}') + 1

        # Extract the JSON string
        json_string = output[start_idx:end_idx]

        print(json_string)
        
        # Load JSON data
        json_data = json.loads(json_string)

        return json_data
    
    except json.JSONDecodeError as e:
        print("Error decoding JSON.", e)
        return 'Cannot summarize review'
    except Exception as e:
        print("Error decoding JSON.", e)
        return str(e)


