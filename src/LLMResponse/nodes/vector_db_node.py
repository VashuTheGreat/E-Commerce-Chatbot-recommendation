from utils.asyncHandler import asyncHandler
from src.LLMResponse.entity import State
import pickle
import os

@asyncHandler
async def vector_db_node(state: State):
    db_path = "./data/db.pkl"
    if not os.path.exists(db_path):
        state.db_res = []
        return state
    with open(db_path, "rb") as f:
        vector_db = pickle.load(f)
    results = vector_db.similarity_search(state.llm_query, k=3)
    clean = []
    for item in results:
        clean.append({
            "page_content": item.page_content,
            "metadata": item.metadata
        })
    state.db_res = clean
    return state
