from setuptools import find_packages, setup

setup(
    name='bedrock_fm',
    packages=find_packages(include=['bedrock_fm', 'bedrock_fm*']),
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