# chalicelib/settings.py
import os

DATABASE = {
    'HOST': 'aws-genai.3nqbckj.mongodb.net',
    'USER': 'fibeg',
    'PASSWORD': '0iEsrkUgoOfdA5jo',
    'COLLECTION': 'sales',
    'NAME': 'supply_store'
}

# DB = {
#     'HOST': os.environ['DB_HOST'],
#     'USER': os.environ['DB_USER'],
#     'PASSWORD': os.environ['DB_PASSWORD']
#     'COLLECTION': 'sales',
#     'NAME': 'supply_store'
# }