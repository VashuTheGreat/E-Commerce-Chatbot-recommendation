import asyncio
import sys
import os
from unittest.mock import patch, AsyncMock, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pipelines.graph_runner_pipeline import GraphRunnerPipeline
from langchain_core.messages import AIMessage


async def main():
    pipeline = GraphRunnerPipeline()
    query = "Show me similar products"
    image_path = "/home/vashuthegreat/Projects/E-Commerce-Chatbot-recommendation/data/test1.png"

    orchestrator_output = MagicMock()
    orchestrator_output.redirect_to = "chat_node"
    orchestrator_output.querie = "test query"

    chat_response = AIMessage(content="Here are some products you might like!")

    with patch("src.nodes.agents_nodes.llm") as mock_llm:
        structured_llm = MagicMock()
        structured_llm.ainvoke = AsyncMock(return_value=orchestrator_output)
        mock_llm.with_structured_output.return_value = structured_llm

        tools_llm = MagicMock()
        tools_llm.ainvoke = AsyncMock(return_value=chat_response)
        mock_llm.bind_tools.return_value = tools_llm

        result = await pipeline.initiate("test-thread-1", query, image_path)
        print("Graph result keys:", list(result.keys()))
        print("Redirect to:", result.get("redirect_to"))
        print("Messages count:", len(result.get("messages", [])))
        if result.get("messages"):
            print("Last message:", result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
