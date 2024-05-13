#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import json
import urllib.request

apigateway_url = 'https://n6x93z1ekf.execute-api.us-west-2.amazonaws.com/'
headers = {
    'Content-Type': 'application/json'
}

def get_named_parameter(event, name):
    return next(item for item in event['parameters'] if item['name'] == name)['value']


def get_named_property(event, name):
    return next(
        item for item in
        event['requestBody']['content']['application/json']['properties']
        if item['name'] == name)['value']

def invoke_url(path):
    url = apigateway_url + path
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

def get_product_by_id(event):
    return invoke_url('products/id/' + get_named_parameter(event, 'productId'))

def get_featured_products():
    return invoke_url('products/featured')

def create_order(event):
    username = get_named_parameter(event, 'username')
    order = {
        'username': username,
        'items': get_named_property(event, 'items')
    }
    return invoke_url('orders', json.dumps(order).encode('utf-8'))

def get_order_by_id(event):
    return invoke_url('orders/id/' + get_named_parameter(event, 'orderId'))

def get_orders_by_username(event):
    return invoke_url('orders/username/' + get_named_parameter(event, 'username'))


def lambda_handler(event, context):
    print(event)
    action = event['actionGroup']
    api_path = event['apiPath']

    if api_path == '/products/id/{productId}':
        body = get_product_by_id(event)
    elif api_path == '/products/featured':
        body = get_featured_products()
    elif api_path == '/orders':
        body = create_order(event)
    elif api_path == '/orders/id/{orderId}':
        body = get_order_by_id(event)
    elif api_path == '/orders/username/{username}':
        body = get_orders_by_username(event)
    else:
        body = {"{}::{} is not a valid api, try another one.".format(action, api_path)}

    response_body = {
        'application/json': {
            'body': str(body)
        }
    }

    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        'httpMethod': event['httpMethod'],
        'httpStatusCode': 200,
        'responseBody': response_body
    }

    response = {'response': action_response}
    return response