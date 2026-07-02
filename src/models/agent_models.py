from pydantic import BaseModel, Field
from typing import List, Literal,Optional
from langgraph.graph.message import MessagesState

class State(MessagesState):
    user_query: str = ""
    image_path: str = ""
    image_summary: str = ""
    llm_query: str = ""
    db_res: List[dict] = []
    summary: str = ""
    redirect_to: str = ""
    query_for_db_search: str = ""
    top_k: int = 5
    img_caption:Optional[str] = None



class Product_type(BaseModel):
    pass

class Orchastrator_Output(BaseModel):
    redirect_to: Literal['chat_node', 'retreiver_node'] = Field(
        'chat_node',
        description="This model redirects to chat_node for casual talk or to retreiver_node for product retrieval."
    )
    querie: str = Field(
        default="",
        description="Search query for database retrieval."
    )




class Exact_Matcher_State(BaseModel):
    image_path: str = ""
    query_for_db_search: str = ""
    top_k: int = 5
    img_caption: Optional[str] = None
    db_res: List[dict] = []
