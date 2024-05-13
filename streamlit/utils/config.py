import os, requests
import os, requests
from dotenv import load_dotenv
import streamlit as st
import yaml

# Load environment variables from .env file during local development
def loadEnv():
    if os.path.exists('./.env'):
        #print(f'.env.local exists: {os.path.exists("./.env.local")}')
        #load_dotenv(dotenv_path='./.env.local', override= True)
        load_dotenv()
        

@st.cache_resource(ttl=1800)
def getEnvCredentials():
    loadEnv()
    key = os.environ.get('AWS_ACCESS_KEY_ID', '')
    secret = os.environ.get('AWS_SECRET_ACCESS_KEY','')
    region = os.environ.get('AWS_DEFAULT_REGION','eu-west-1')
    credentials_relative_uri = os.environ.get('AWS_CONTAINER_CREDENTIALS_RELATIVE_URI','')
    sessionToken = None

    # logger.info(f'key: {key}')
    # logger.info(f'secret: {secret}')
    # logger.info(f'region: {region}')

    credentials_url = f'http://169.254.170.2{credentials_relative_uri}'
    if credentials_relative_uri != '':
        response = requests.get(credentials_url)
        response_json = response.json()
        #logger.info(f'response_json: {response_json}')
        key = response_json['AccessKeyId']
        secret = response_json['SecretAccessKey']
        sessionToken = response_json['Token']

        # logger.info(f'new key: {key}')
        # logger.info(f'new secret: {secret}')

    print(f'ENCV: {key}, {secret}, {region}')
    
    #print(f'ENCV: {os.environ["AWS_ACCESS_KEY_ID"]}, { os.environ["AWS_SECRET_ACCESS_KEY"]}, {region}')

    return key, secret, region, sessionToken

@st.cache_resource
def getOpenSearchConfig():
    endpoint = os.environ.get('OS_ENDPOINT', '')
    username = os.environ.get('OS_USERNAME','')
    password = os.environ.get('OS_PASSWORD','')

    #print(f'OpenSearch: {endpoint}, {username}, {password}')

    return endpoint, username, password

@st.cache_resource
def getBedrockConfig():
    br_endpoint = os.environ.get('BR_ENDPOINT', '')
    br_region = os.environ.get('BR_REGION','us-west-2')
    br_assume_role = os.environ.get('BR_ASSUME_ROLE', None)

    #br_endpoint = ''
    #br_region = 'us-east-1'

    #print(f'Bedrock: {br_endpoint}, {br_region}')

    return br_endpoint, br_region, br_assume_role

@st.cache_resource
def load_config():
    config = ''
    # Load the configuration from config.yaml
    with open('config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)
    return config
