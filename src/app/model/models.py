from pydantic import BaseModel
from typing import Dict, List, Union



class CardProduct(BaseModel):
    url: str
    vendor_code: int


class Characteristic(BaseModel):
    value: str
    description: str


class Product(BaseModel):
    url: str
    vendor_code: int
    name: str
    price: float
    rating: int
    description: str | None
    сharacteristics: List[Characteristic]
    photos: List[str]
    category: str


class Products(BaseModel):
    products: List[Product]