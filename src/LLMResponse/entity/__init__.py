from pydantic import BaseModel, Field
from typing import List, Optional

class Product(BaseModel):
    gender: Optional[str] = None
    masterCategory: Optional[str] = None
    subCategory: Optional[str] = None
    ArticleType: Optional[str] = None
    BaseColor: Optional[str] = None
    season: Optional[str] = None
    usage: Optional[str] = None
    productDisplayName: Optional[str] = None

class ImageComponents(BaseModel):
    image_discription: List[Product]

class State(BaseModel):
    user_query: Optional[str] = None
    image_path: Optional[str] = None
    image_summary: Optional[str] = None
    llm_query: Optional[str] = None
    db_res: List[dict] = Field(default_factory=list)
    summary: Optional[str] = None
