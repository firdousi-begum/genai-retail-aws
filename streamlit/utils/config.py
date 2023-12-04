import os, requests, base64
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file during local development
def loadEnv():
    if os.path.exists('./.env.local'):
        #print(f'.env.local exists: {os.path.exists("./.env.local")}')
        load_dotenv(dotenv_path='./.env.local', override= True)
        

@st.cache_resource
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

    #br_endpoint = ''
    #br_region = 'us-east-1'

    #print(f'Bedrock: {br_endpoint}, {br_region}')

    return br_endpoint, br_region

def get_img_as_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

@st.cache_data  
def get_background():
    bg_img = get_img_as_base64("images/bg.png")
    logo = get_img_as_base64("images/logo.png")

    page_bg_img = f"""
    <style>
    .imglogo {{
    width: 100%;
    height: auto; 
    content:
    }}
    .stApp {{
    background-image: url("data:image/png;base64,{bg_img}");
    background-size: cover;
    }}

    [data-testid="stHeader"] {{
    background-color: rgba(0, 0, 0, 0);
    }}

   [data-testid="stHeader"]{{
    # background-image: url("data:image/png;base64,{logo}");
    # background-repeat: no-repeat;
    # background-size: 100% 100%;  
    # background-position: 50% 0%;
    background: url("data:image/png;base64,{logo}") 6% center/138px no-repeat, linear-gradient(to right, rgb(36,34,67) 40%,rgb(76,19,138) 70%, rgb(205,54,117));
    display: flex;
    align-items: center;
    justify-content: center;
    }}

    [data-testid="stSidebar"] {{
    #background-color: rgba(0, 0, 0, 0);
    # background-image: url("data:image/png;base64,{logo}"), url("data:image/png;base64,{bg_img}");
    # background-position: center 30px, center center;
    # background-repeat: no-repeat, no-repeat;
    # background-image: url("data:image/png;base64,{logo}");
    # background-position: center 30px;
    # background-repeat: no-repeat;
    # background-size: 138px;
    # position:relative;
      
    }}

    [data-testid="stSidebarNav"] {{
    background-image: url("data:image/png;base64,{logo}");
    background-position: center 30px;
    background-repeat: no-repeat;
    background-size: 138px;
    # position:relative;
      
    }}

    [data-testid="baseButton-secondary"] {{
    box-shadow: inset 0px -5px 5px 0px rgba(0, 0, 0, 0.5);
    background: linear-gradient(to bottom, rgb(143, 10, 86) ,rgb(168, 45, 97), rgb(143, 10, 86));

    }}

    [data-testid="baseButton-secondary"]:active {{
    transform: translateY(1px);
    #background-color: #230930;
    box-shadow: inset 0px 10px 20px 2px rgba(0, 0, 0, 0.25);
    }}

    [data-testid="stImage"] {{
    box-shadow: -5px -10px 10px rgba(0, 0, 0,0.5);
    border-radius: 5px;
    }}

    </style>
    """

    st.markdown(page_bg_img, unsafe_allow_html=True)

