#!/usr/bin/env python3
"""Entrypoint to the cognito alb fargate demo CDK app"""
import os
import aws_cdk as core

from genai_retail_stack import GenAiRetailStack
from configuration import get_config

# Set the AWS account and region
account = os.environ.get('CDK_DEFAULT_ACCOUNT')
region = os.environ.get('CDK_DEFAULT_REGION')

# Create an environment object with the specified account and region
env = core.Environment(account=account, region=region)

def main():
    """Wrapper for the CDK app"""
    app = core.App()

    GenAiRetailStack(
        app,
        "genai-retail-fargate",
        config=get_config(),
        env=env
    )

    app.synth()


if __name__ == "__main__":
    main()
