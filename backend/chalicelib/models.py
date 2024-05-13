from dataclasses import dataclass
from datetime import datetime
from typing import List
import json
from dataclasses import asdict

@dataclass
class Customer:
    name: str
    age: int
    email: str
    statisfaction: int

@dataclass
class Item:
    name: str
    price: float
    quantity: int

@dataclass
class Sale:
    orderId: str
    status: str
    saleDate: datetime
    storeLocation: str
    couponUsed: bool
    purchaseMethod: str
    customer: Customer
    items: List[Item]

# Define a custom JSON encoder to handle data class serialization
class DataClassEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__dict__'):
            return asdict(obj)
        return super().default(obj)
    
# Define a custom JSON encoder to handle data class serialization
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, '__dict__'):
            return asdict(obj)
        return super().default(obj)