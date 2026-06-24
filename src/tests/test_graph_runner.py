import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.pipelines.graph_runner_pipeline import GraphRunnerPipeline

async def main():
    pipeline = GraphRunnerPipeline()
    print("Testing with image:")
    res_img = await pipeline.initiate(
        "thread-1",
        "Show me similar products",
        "/home/vashuthegreat/Projects/E-Commerce-Chatbot-recommendation/data/test1.png"
    )
    print("Keys:", list(res_img.keys()))
    print("Redirect:", res_img.get("redirect_to"))
    if res_img.get("messages"):
        print("Last message:", res_img["messages"][-1].content)

    print("\nTesting without image:")
    res_no_img = await pipeline.initiate(
        "thread-2",
        "Hello, how can I find a good watch?",
        ""
    )
    print("Keys:", list(res_no_img.keys()))
    print("Redirect:", res_no_img.get("redirect_to"))
    if res_no_img.get("messages"):
        print("Last message:", res_no_img["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
