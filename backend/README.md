# Demo application for a recipes assistant

**NOTE:** this code is provided as-is and is not to be considered in any way as production grade. 
In particular no special attention has been paid to protect the deployed API, which will be open to everybody knowing the endpoint.


## Deployment

Clone the repo or unzip the file in a new folder and move into that folder.


### Backend

The backend is AWS Lambda function deployed via Chalice behind an API Gateway (unsecured).
The code of the lambda function can be found in `app.py`.

This demo uses Amazon Bedrock in `us-west-2`. If you have enabled Bedrock in a different region, update line 17 in `app.py`. You also need to have activated Anthropic Claude Instant v1 via the Bedrock console.

To deploy to your AWS account execute. If you have any issues check the Chalice documentation.

```
cd backend
pip install chalice
pip install -r requirements.txt
chalice deploy
chalice url
```

Once done, you'll have an URL printed on the terminal, like:

```https://xp12234455.execute-api.eu-west-1.amazonaws.com/api/```

Note it down.

### Frontend

The frontend is a Tampermonkey script that uses a React GUI component.

Open the `frontend/src/config.js` file and replace the URL with the backend URL. Save the file.

In the `frontend` folder, run:

```
npm i
npn run dev
```

This will run a dev server on the local machine providing the Tampermonkey script. To use it, create a new script in the browser Tampermonkey addon and copy paste the `dist/dev.user.js` file content. 
Save and browse to a recipe, such as https://www.hemkop.se/recept/moules_rotfrukter.


If you want to use the assistant without having the dev server running, you can instead create the Tampermonkey script using `dist/bundle.user.js` file.


## Notebook

In the root folder there is a Jupyter notebook with the same code that runs in the backend. To use the notebook, create a new virtual environment via `poetry install` or execute the `pip` instructions at the top of the notebook.
