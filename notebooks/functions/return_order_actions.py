#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import json
import os
import uuid
import datetime
import random
from faker import Faker

# Initialize Faker
fake = Faker()

def generate_dummy_order(email, date, order_id, shipping_address):
    shopping_items = [
        "Laptop", "Smartphone", "Headphones", "Keyboard", "Mouse", "Monitor", 
        "Printer", "Camera", "Speakers", "Router", "Tablet", "Smartwatch", 
        "External Hard Drive", "USB Flash Drive", "Charger", "Backpack", 
        "Desk Lamp", "Webcam", "Microphone", "Gaming Console", "Sunglass",
        "Running Shoes", "Water Bottle"
    ]

    order_items = [
        {
            "productId": fake.uuid4(),
            "productName": random.choice(shopping_items),
            "quantity": random.randint(1, 10),
            "price": round(random.uniform(10.0, 100.0), 2)
        }
        for _ in range(random.randint(1, 5))
    ]

    total_price = round(sum(item['quantity'] * item['price'] for item in order_items), 2)

    order = {
        "id": order_id,
        "email": email,
        "orderDate": date,
        "order": {
            "orderItems": order_items,
            "shippingAddress": shipping_address
        },
        "totalAmount": total_price
    }

    return order

def get_user_orders(email):
    order_id = fake.uuid4()
    date = datetime.date.today().strftime("%Y-%m-%d")
    first_name = fake.first_name()
    last_name = fake.last_name()
    address = fake.street_address()
    city = fake.city()
    zip_code = fake.zipcode()
    state = fake.state()
    country = fake.country()

    shipping_address = {
        "firstName": first_name,
        "lastName": last_name,
        "address": address,
        "city": city,
        "zipCode": zip_code,
        "state": state,
        "country": country
    }

    # Generate a random number of orders
    number_of_orders = random.randint(1, 5)
    dummy_orders = []

    for _ in range(number_of_orders):
        order_id = fake.uuid4()
        order = generate_dummy_order(email, date, order_id, shipping_address)
        dummy_orders.append(order)
        date = (date- datetime.timedelta(days=10)).strftime("%Y-%m-%d")

    return dummy_orders


def lambda_handler(event, context):
    print(event)
    action = event['actionGroup']
    api_path = event['apiPath']
    http_method = event['httpMethod']

    if api_path == "/order/{orderId}/return" and http_method == "POST":
        body = return_order(event)
    elif api_path == "/orders/user/{email}" and http_method == "GET":
        body = get_orders_by_user(event)
    elif api_path == "/orders/{orderId}/return/sendEmail" and http_method == "POST":
        body = send_order_return_email(event)
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

def get_named_parameter(event, name):
    return next(item for item in event['parameters'] if item['name'] == name)['value']

def get_named_property(event, name):
    return next(
        item for item in
        event['requestBody']['content']['application/json']['properties']
        if item['name'] == name)['value']

def get_orders_by_user(event):
    return get_user_orders(get_named_parameter(event, 'email'))

def return_order(event):
    order_id = get_named_parameter(event, 'productId')
    email = get_named_property(event,"email")
    order_items_str = get_named_property(event,"orderItems")
    first_name = get_named_property(event,"firstName")
    last_name = get_named_property(event,"lastName")

    try:
        order_items = json.loads(order_items_str)
    except (json.JSONDecodeError, KeyError, TypeError):
        # Handle the case where order_details is not a valid JSON string or doesn't have the expected structure
        return {"error": "Invalid order details format"}
    
    return {
        "referenceId": str(uuid.uuid4()),
        "orderDetails": order_items
    }

def send_order_return_email(event):
    email = get_named_property(event,"email")
    email_body = get_named_property(event,"emailBody")
    order_id = get_named_parameter(event,"orderId")

    # Validate required fields
    if not all([email, email_body, order_id]):
        raise ValueError("Missing required fields in the request body")
    
    # sendEmail(email, f"Order Confirmation for {order_id}", email_body)

    return f"Order return registration email sent successfully to {email}"

# def sendEmail(email, subject, body):
#     # Implement email sending logic here
#     ses_client = boto3.client("ses")
#     response = ses_client.send_email(
#       Source="your_source_email@example.com",
#       Destination={
#           "ToAddresses": [email]
#       },
#       Message={
#           "Subject": {
#               "Data": subject
#           },
#           "Body": {
#               "Text": {
#                   "Data": body
#               }
#           }
#       }
#     )
