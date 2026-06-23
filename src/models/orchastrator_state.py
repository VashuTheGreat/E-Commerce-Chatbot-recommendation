import logging
from typing import List, Optional
from langgraph.graph.message import MessagesState


class State(MessagesState):
    analyse_content_paths: List[str] = []
    uploaded_content_analysis: List[dict] = []
    db_results: List[dict] = []
    final_response: Optional[str] = None
    search_query: str = ""
    query_type: str = ""

logging.debug("State model loaded - extends MessagesState with analyse_content_paths, uploaded_content_analysis, db_results, final_response, search_query, query_type")
