from pydantic import BaseModel,Field

from typing import Literal

class Product(BaseModel):
    gender:str=Literal['Men','Woman','Unisex']
    masterCategory:str=Field(...,discriminator="""
eg:-
                             Topwear,
                             Bootomwear
                             Flip Flops
                             etc
""")
    subCategory:str=Field(...,discriminator="""

eg:-
                          Topwear
                          etc.
""")
    
    ArticleType:str=Field(...,discriminator="""

eg Shirts

""")
    
    BaseColor:str=Field(...,discriminator="""

eg Navy Blue

""")
    season:str=Field(...,discriminator="""
Fall

""")
    
    usage:str=Field(...,discriminator="""
Casual

""")
    productDisplayName:str=Field(...,discriminator="""
Turtle Check Men Navy Blue Shirt

""")
  

class ImageComponents(BaseModel):
    image_discription:List[Product]
