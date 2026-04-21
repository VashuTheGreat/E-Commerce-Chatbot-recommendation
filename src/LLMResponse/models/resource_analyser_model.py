from pydantic import BaseModel
from typing import Optional, List


class Product(BaseModel):
    gender: Optional[str] = None
    masterCategory: Optional[str] = None
    subCategory: Optional[str] = None
    articleType: Optional[str] = None
    baseColor: Optional[str] = None
    season: Optional[str] = None
    usage: Optional[str] = None
    productDisplayName: Optional[str] = None


class ProductModels(BaseModel):
    product_description: List[Product]