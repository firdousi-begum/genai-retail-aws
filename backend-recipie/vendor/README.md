## bedrock_fm

**Convenience classes to interact with Bedrock Foundation Models**

Bedrock provides a unified API to invoke foundation models in the form of `bedrock.invoke_model()` and `bedrock.invoke_model_with_response_stream()`. This unified methods require a `modelId` and a stringified JSON `body` containing the model specific input parameters. Additional parameters, such as `accept`, and `contentType` can also be specified.

This simplicity comes at the cost that developers need to know the model specific format of the `body` payload. Moreover, the payloads being completely different, does not allow to easy swapping out a model for another.

This library exposes a separate class for each of the Bedrock models, with an simpler `generate()` APIs. To get a stream instead of a full completion you can pass the parameter `stream=True`. To obtain a detailed response including the original prompt, the body passed to the `invoke_*` method and timing information you can pass the parameter `details=True`. The API is fully typed, including the different return types based on the `stream` and `details` parameters values.

The output generation can also be tuned with the additional `temperature`, `top_p` and `stop_words` parameters which can be passed at the instance creation time (in the class constructor) and overridden at generation time in the `generate` and `stream` methods.  

All models create a `boto3` client at the time of instantiation. To customize the client creation one can use environment variables (such as `AWS_PROFILE`, `AWS_DEFAULT_REGION`, etc) or by invoking `boto3.setup_default_session()` method before the foundation model instances are created.

Model specific parameters can be provided via the `extra_args` parameters as a Dict, both in the constructors and in the `generate` and `stream` methods (and their `_details` variants). It is strongly advised to specify the `extra_args` in the constructor of the foundation model class, in order to keep the code as agnostic as possible.

### Build the wheel

This project uses [poetry](https://python-poetry.org/). Follow their [instructions to install](https://python-poetry.org/docs/#installation).

Clone the repo and build the wheel via:

```
poetry build
```

This will create a wheel in `./dist/` folder that you can then install in your own project via `pip` or `poetry`

### Use

**Basic use**

```py
from bedrock_fm import TitanLarge

fm = Titan()
fm.generate("Hi. Tell me a joke?")
```

**Streaming**

```py
from bedrock_fm import ClaudeV1Instant

fm = ClaudeV1Instant()
for t in fm.generate("Hi. Tell me a joke?", stream=True):
    print(t)
```

**boto3 customization**

```py
from bedrock_fm import Titan
import boto3

boto3.setup_default_session(region_name='us-east-1')
fm = Titan()
```

**Common Foundation Model parameters**

```py
from bedrock_fm import ClaudeV1Instant

# You can setup parameters at the model instance level
fm = ClaudeV1Instant(temperature=0.5, top_p=1)
# You can override parameters value when invoking the generation functions - also for stream
print(fm.generate("Hi. Tell me a joke?", token_count=100)[0])

```

**Model specific parameters**

```py
from bedrock_fm import ClaudeV1Instant

# Set up extra parameter for the model instance
fm = ClaudeV1Instant(extra_args={'top_k': 200})
for t in fm.generate("Hi. Tell me a joke?", stream=True):
    print(t)

# Override the instance parameters
# NOTE: this is not recommended since these lines of code
#       would only work with this model family
for t in fm.generate("Hi. Tell me a joke?", stream=True, extra_args={'top_k': 400}):
    print(t)
```

**Get inference details**

```py
from bedrock_fm import ClaudeInstantV1

fm = ClaudeInstantV1()

print(fm.generate("Tell me a joke?", details=True))

""""
CompletionDetails(output=['Sorry - this model is designed to avoid potentially inappropriate content. Please see our content limitations page for more information.'], response={'inputTextTokenCount': 4, 'results': [{'tokenCount': 31, 'outputText': 'Sorry - this model is designed to avoid potentially inappropriate content. Please see our content limitations page for more information.', 'completionReason': 'CONTENT_FILTERED'}]}, prompt='Tell me a joke', body='{"inputText": "Tell me a joke", "textGenerationConfig": {"maxTokenCount": 500, "stopSequences": [], "temperature": 0.7, "topP": 1}}', latency=1.531674861907959)
"""
```

**Titan embeddings**

```py

from bedrock_fm import TitanEmbeddings

print(TitanEmbeddings().generate("Tell me a joke"))
```

## Throttling

To cope with throttling exceptions you can use libraries like [backoff](https://pypi.org/project/backoff/)

```python
import backoff

@backoff.on_exception(backoff.expo, br.exceptions.ThrottlingException)
def generate(prompt):
    return fm.generate(prompt)

...
    generate("Hello how are you?")

```

### Alternate method to build the bedrock_fm Helper

To use the same helper class in your Jupyter notebook, package into wheel library
1. Naviagte to "backend/vendor" folder where you are going to create your Python library in
2. Create virtual environment and activate it

```
python3 -m venv venv
source venv/bin/activate

```
3. In your environment, make sure you have pip installed wheel, setuptools and twine. We will need them for later to build our Python library.
```
pip install wheel
pip install setuptools
pip install twine
```
4. Create setup.py
```
from setuptools import find_packages, setup

setup(
    name='bedrock_fm',
    packages=find_packages(),
    version='0.1.0',
    python_requires='>=3.9',
    description='Bedrock Foundational Models Wrapper',
    author='Begum Firdousi Abbas',
    license='MIT',
    install_requires=[
        'boto3>=1.28.57',
        'botocore>=1.31.57',
        'attrs>=23.1.0,<24.0.0'
    ],
    classifiers=[

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
],
)
```

5. Now that all the content is there, we want to build our library. Make sure your present working directory is "backend/vendor" folder. In your command prompt, run:
```
python setup.py bdist_wheel
```

6. The final wheel package will now be generated under "dist" folder in "vendor" directory. You can now pip install

7. Deactivate virtual python environment
```
deactivate
```