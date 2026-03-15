from pydantic import BaseModel, Field
from typing import List, Optional, Any

class State(BaseModel):
    user_query: Optional[str] = Field(default=None)
    image_path: Optional[str] = Field(default=None)
    image_summary: Optional[str] = Field(default=None)
    llm_query: Optional[str] = Field(default=None)
    db_res: List[dict] = Field(default_factory=list)
    summary: Optional[str] = Field(default=None)
