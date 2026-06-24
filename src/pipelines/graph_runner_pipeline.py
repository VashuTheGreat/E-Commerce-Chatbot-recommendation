from langchain_community.vectorstores import yellowbrick
import logging
from src.components.graph_runner import GraphRunner

class GraphRunnerPipeline:
    def __init__(self):
        logging.info("GraphRunnerPipeline - initializing graph runner pipeline")
        self.runner = GraphRunner()

    async def initiate(self, thread_id: str, query: str, image_path: str = ""):
        logging.info(f"GraphRunnerPipeline - initiating run request for thread_id: {thread_id}")
        async for chunk in self.runner.run(thread_id,query,image_path):
            yield chunk
        logging.info("GraphRunnerPipeline - run completed. returning result.")
