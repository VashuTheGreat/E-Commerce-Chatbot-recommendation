from pydantic import BaseModel, Field
from typing import List, Optional

class Product(BaseModel):
    id: Optional[str] = Field(None, description="The unique ID of the product")
    gender: Optional[str] = Field(None, description="Target gender for the product")
    masterCategory: Optional[str] = Field(None, description="Main category of the product")
    subCategory: Optional[str] = Field(None, description="Sub-category of the product")
    articleType: Optional[str] = Field(None, description="Type of the article")
    baseColour: Optional[str] = Field(None, description="Base color of the product")
    season: Optional[str] = Field(None, description="Season the product is intended for")
    usage: Optional[str] = Field(None, description="Intended usage of the product")
    productDisplayName: Optional[str] = Field(None, description="Display name of the product")

class ImageAnalysis(BaseModel):
    summary: str = Field(..., description="Summary of all products in the image")
    products: List[Product] = Field(default_factory=list, description="List of detected products")
