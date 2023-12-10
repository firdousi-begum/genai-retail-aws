# chalicelib/db.py
import json
from chalicelib import settings
from chalicelib.models import Sale, Customer, Item, CustomJSONEncoder
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = f"mongodb+srv://{settings.DATABASE['USER']}:{settings.DATABASE['PASSWORD']}@{settings.DATABASE['HOST']}/?retryWrites=true&w=majority"
collectionName = settings.DATABASE['COLLECTION']
dbName = settings.DATABASE['NAME']

class MongoDb():
    def __init__(self):
        self.mongoClient = MongoClient(uri, server_api=ServerApi('1'))
        self.client = self.mongoClient[dbName][collectionName]
    
    def getItems(self):
        result = self.client.find(limit=10)
        sales = []

        if result:
            for doc in result:
                customer_data = doc.get('customer', {})
                items_data = doc.get('items', [])
                customer = Customer(**customer_data)
                items = [Item(**item_data) for item_data in items_data]
                sale = Sale(
                    orderId=doc.get('orderId'),
                    status=doc.get('status'),
                    saleDate=doc.get('saleDate'),
                    storeLocation=doc.get('storeLocation'),
                    couponUsed=doc.get('couponUsed'),
                    purchaseMethod=doc.get('purchaseMethod'),
                    customer=customer,
                    items=items
                )
                sales.append(sale)

        else:
            sales.append("No documents found.")

        # Serialize the 'sales' list to JSON using the custom encoder
        sales_json = json.dumps(sales, cls=CustomJSONEncoder, indent=2)
        sales_obj = json.loads(sales_json)

        return sales_obj
    
    def getItemsByStatus(self, status):
        result = self.client.find({
            "status" : status
        }).limit(2)
        sales = []

        if result:
            for doc in result:
                customer_data = doc.get('customer', {})
                items_data = doc.get('items', [])
                customer = Customer(**customer_data)
                items = [Item(**item_data) for item_data in items_data]
                sale = Sale(
                    orderId=doc.get('orderId'),
                    status=doc.get('status'),
                    saleDate=doc.get('saleDate'),
                    storeLocation=doc.get('storeLocation'),
                    couponUsed=doc.get('couponUsed'),
                    purchaseMethod=doc.get('purchaseMethod'),
                    customer=customer,
                    items=items
                )
                sales.append(sale)

        else:
            sales.append("No documents found.")

        # Serialize the 'sales' list to JSON using the custom encoder
        sales_json = json.dumps(sales, cls=CustomJSONEncoder, indent=2)
        sales_obj = json.loads(sales_json)

        return sales_obj
    
    def getItemsByOrderId(self, orderId):
        result = self.client.find({
            "orderId" : orderId
        })
        sales = []

        if result:
            for doc in result:
                customer_data = doc.get('customer', {})
                items_data = doc.get('items', [])
                customer = Customer(**customer_data)
                items = [Item(**item_data) for item_data in items_data]
                sale = Sale(
                    orderId=doc.get('orderId'),
                    status=doc.get('status'),
                    saleDate=doc.get('saleDate'),
                    storeLocation=doc.get('storeLocation'),
                    couponUsed=doc.get('couponUsed'),
                    purchaseMethod=doc.get('purchaseMethod'),
                    customer=customer,
                    items=items
                )
                sales.append(sale)

        else:
            sales.append("No documents found.")

        # Serialize the 'sales' list to JSON using the custom encoder
        sales_json = json.dumps(sales, cls=CustomJSONEncoder, indent=2)
        sales_obj = json.loads(sales_json)

        print('got sales object')

        return sales_obj


    def __del__(self):
        self.mongoClient.close()