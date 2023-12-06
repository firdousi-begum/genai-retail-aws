#!/usr/bin/env python3
"""Entrypoint to the cognito alb fargate demo CDK app"""
import os
import aws_cdk as core

from genai_retail_stack import GenAiRetailStack, CertificateStack
from configuration import get_config

# Set the AWS account and region
account = os.environ.get('CDK_DEFAULT_ACCOUNT')
region = os.environ.get('CDK_DEFAULT_REGION')

# Create an environment object with the specified account and region
env = core.Environment(account=account, region=region)
env_us = core.Environment(account=account, region="us-east-1")

def main():
    """Wrapper for the CDK app"""
    app = core.App()

    cert_stack = CertificateStack(
        app,
        "genai-retail-cert-stack",
        config=get_config(),
        env=env_us,
        cross_region_references=True
    )

    GenAiRetailStack(
        app,
        "genai-retail-fargate",
        config=get_config(),
        certificate=cert_stack.main_cert,
        env=env,
        cross_region_references=True
    )

    app.synth()


if __name__ == "__main__":
    main()
