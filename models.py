from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    id: Optional[int] = None
    name: str
    description: str  
    price: float
    quantity: int

    class Config:
        from_attributes = True
