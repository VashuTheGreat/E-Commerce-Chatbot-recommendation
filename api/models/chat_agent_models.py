from pydantic import BaseModel

class ChatAgentModel(BaseModel):
    message: str
    thread_id: str
    