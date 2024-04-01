from pydantic import BaseModel
from typing import Dict, List, Union



class CardProduct(BaseModel):
    url: str


class Characteristic(BaseModel):
    value: str
    description: str


class Product(BaseModel):
    url: str
    vendor_code: int
    name: str
    price: int
    rating: int
    description: str | None
    сharacteristics: List[Characteristic]
    photos: List[str]


class Products(BaseModel):
    products: List[Product]