from langchain_community.vectorstores import yellowbrick
import json
import logging
from src.components.graph_runner import GraphRunner

class GraphRunnerPipeline:
    def __init__(self):
        logging.info("GraphRunnerPipeline - initializing graph runner pipeline")
        self.runner = GraphRunner()

    @staticmethod
    def _make_serializable(obj):
        if hasattr(obj, "to_json"):
            logging.info("to_json")
            return obj.to_json()
        
        raise TypeError(f"Object of type {type(obj).__name__} is not serializable")

    async def initiate(self, thread_id: str, query: str, image_path: str = ""):
        logging.info(f"GraphRunnerPipeline - initiating run request for thread_id: {thread_id}")
        async for chunk in self.runner.run(thread_id, query, image_path):
            yield f"data: {json.dumps(chunk, default=self._make_serializable)}\n\n"
        logging.info("GraphRunnerPipeline - run completed. returning result.")
