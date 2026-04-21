import logging
from typing import List, Optional, Annotated
from langgraph.graph.message import MessagesState, add_messages
from langchain_core.messages import BaseMessage


class State(MessagesState):
    analyse_content_paths: List[str] = []
    uploaded_content_analysis: List[dict] = []
    db_results: List[dict] = []
    final_response: Optional[str] = None

logging.debug("State model loaded — extends MessagesState with analyse_content_paths, uploaded_content_analysis, db_results, final_response")
