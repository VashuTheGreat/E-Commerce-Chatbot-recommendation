from src.components.graph_runner import GraphRunner

class GraphRunnerPipeline:
    def __init__(self):
        self.runner = GraphRunner()

    async def initiate(self, thread_id: str, query: str, image_path: str = ""):
        result = await self.runner.run(thread_id, query, image_path)
        return result
