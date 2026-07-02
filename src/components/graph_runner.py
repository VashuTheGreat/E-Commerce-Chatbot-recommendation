import logging
from src.graphs.builder import graph
from src.memmory import memory
from langchain_core.messages import HumanMessage

class GraphRunner:
    def __init__(self):
        logging.info("GraphRunner - initializing and loading graph/memory checkpointer")
        self.graph = graph
        self.memory = memory
        

    async def run(self, thread_id: str, query: str, image_path: str = "",top_k:int = 5):
        logging.info(f"GraphRunner - starting run for thread_id: {thread_id}, query: '{query}', image_path: '{image_path}'")
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "user_query": query,
            "image_path": image_path,
            "top_k": top_k,
            "db_res": [],
            "summary": "",
            "redirect_to": "",
            "query_for_db_search": "",
            "image_summary": "",
            "llm_query": "",
            # Only reset img_caption when no image is being uploaded.
            # If image_path is set, omit it so analyse_image_node writes it fresh.
            # If no image, restore None only on truly fresh threads (checkpoint handles the rest).
            **({"img_caption": None} if not image_path else {}),
        }
        logging.info(f"GraphRunner - initial state prepared: {initial_state}")

        async for chunk in self.graph.astream(initial_state, config,stream_mode="updates"):
            yield chunk
        logging.info(f"GraphRunner - graph execution finished.")
