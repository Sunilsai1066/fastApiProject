from pydantic import BaseModel
from typing import Union


class Product(BaseModel):
    id: int
    name: str
    description: Union[str, None] = None
    price: float
    quantity: int
