from src.graphs.builder import graph
from src.memmory import memory
from langchain_core.messages import HumanMessage

class GraphRunner:
    def __init__(self):
        self.graph = graph
        self.memory = memory

    async def run(self, thread_id: str, query: str, image_path: str = ""):
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "user_query": query,
            "image_path": image_path,
            "top_k": 5,
            "db_res": [],
            "summary": "",
            "redirect_to": "",
            "query_for_db_search": "",
            "image_summary": "",
            "llm_query": ""
        }
        result = await self.graph.ainvoke(initial_state, config)
        return result
