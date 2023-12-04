# Python Built-Ins:
import os
import json
from typing import Optional

# External Dependencies:
import boto3
from botocore.config import Config
import logging
import requests

key = os.environ.get('AWS_ACCESS_KEY_ID', '')
secret = os.environ.get('AWS_SECRET_ACCESS_KEY','')
region = os.environ.get('AWS_DEFAULT_REGION','eu-west-1')
credentials_relative_uri = os.environ.get('AWS_CONTAINER_CREDENTIALS_RELATIVE_URI','')
sessionToken = None

# logger.info(f'key: {key}')
# logger.info(f'secret: {secret}')
# logger.info(f'region: {region}')

credentials_url = f'http://169.254.170.2{credentials_relative_uri}'
if not key or not secret:
    response = requests.get(credentials_url)
    response_json = response.json()
    #logger.info(f'response_json: {response_json}')
    key = response_json['AccessKeyId']
    secret = response_json['SecretAccessKey']
    sessionToken = response_json['Token']
    # logger.info(f'new key: {key}')
    # logger.info(f'new secret: {secret}')


s3 = boto3.client('s3',region_name=region,aws_access_key_id=key,aws_secret_access_key=secret)
comprehend = boto3.client('comprehend',region_name=region,aws_access_key_id=key,aws_secret_access_key=secret)

def detect_sentiment_pii(query):
    sentiment = 'POSITIVE'
    pii_list = []
    if query and len(query) > 5:
        sentiment = comprehend.detect_sentiment(Text=query, LanguageCode='en')['Sentiment']
        resp_pii = comprehend.detect_pii_entities(Text=query, LanguageCode='en')
        for pii in resp_pii['Entities']:
            if pii['Type'] not in ['NAME', 'AGE', 'ADDRESS','DATE_TIME']:
                pii_list.append(pii['Type'])
        if len(pii_list) > 0:
            answer = "I am sorry but I found PII entities " + str(pii_list) + " in your query. Please remove PII entities and try again."
            return answer
        else:
            answer = "Insufficient search query. Please expand the query and/or add more context."
    
    query_type = ''
    if "you" in query:
        query_type = "BEING"

    if query in ["cancel","clear"]:
        answer = 'Thanks come back soon...'
        return answer

    elif sentiment == 'NEGATIVE':
        answer = 'I apologize but I do not answer questions that are negatively worded or that concern me. Kindly rephrase your question and try again.'
        return answer
    
    elif query_type == "BEING":
        answer = 'I apologize but I do not answer questions that are negatively worded or that concern me. Kindly rephrase your question and try again.'
        return answer