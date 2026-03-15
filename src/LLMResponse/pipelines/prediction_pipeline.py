from src.LLMResponse.graphs.chat_graph import graph
from src.LLMResponse.entity import State
import os

async def run_llm_response_pipeline(user_query: str, thread_id: str):
    image_path = f"./tempImage/{thread_id}.jpg"
    
    initial_state = State(
        user_query=user_query,
        image_path=image_path if os.path.exists(image_path) else None
    )
    
    config = {"configurable": {"thread_id": thread_id}}
    
    result = await graph.ainvoke(initial_state, config=config)
    return result
