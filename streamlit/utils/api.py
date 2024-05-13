import requests, os
import json
from urllib.parse import urljoin


class GenAIRetailAPI():

    def __init__(self, logger = None):
        self.api_url = os.environ.get('API_URL', '')
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.logger = logger
    
    def get_text(self, prompt, **args):
        payload = {
            "prompt": prompt,
            **args
        }
        
        api = urljoin(self.api_url, "generate")
        print('API URL: '+ api)
        
        try:
            response = requests.post(api, headers=self.headers, data=json.dumps(payload))
            # Check the response status and content
            if response.status_code == 200:
                result = response.json()[0]
                print(f"API response: {result}")
                return result
            else:
                print(f"API request failed with status code {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Error in API request: {e}")
            return None
    
    def summarize_reviews(self, product_name, product_reviews, **args):
        payload = {
            "product_name": product_name,
            "product_reviews": product_reviews,
            **args
        }
        
        api = urljoin(self.api_url, "summarize/reviews")
        print('API URL: '+ api)
        #print(f'Payload: {payload}')
        
        try:
            response = requests.post(api, headers=self.headers, data=json.dumps(payload))
            # Check the response status and content
            if response.status_code == 200:
                result = response.json()
                #print(f"API response: {result}")
                return result
            else:
                print(f"API request failed with status code {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Error in API request: {e}")
            return None